import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import json

# --- Configure API Key ---
# Vercel will get this from your project's Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# --- Helper Functions ---
def extract_youtube_id(url: str) -> str:
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "youtube.com" in url:
        return url.split("v=")[1].split("&")[0]
    raise ValueError("Invalid YouTube URL")

def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([d['text'] for d in transcript_list])
    except Exception as e:
        raise Exception(f"Could not retrieve transcript: {e}")

def summarize_with_gemini(transcript_text: str) -> dict:
    if not GEMINI_API_KEY:
        raise Exception("Gemini API key not set in environment.")

    model = genai.GenerativeModel('gemini-1.5-flash') # Using a standard, efficient model
    
    prompt = f"""Based on the following YouTube transcript, return a brief summary in this JSON format only:
    {{
      "topic_name": "name of topic",
      "topic_summary": "summary of topic"
    }}

    Transcript:
    \"\"\"
    {transcript_text}
    \"\"\""""

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Clean the response if it's wrapped in markdown
    if raw_text.startswith("```json"):
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response as JSON: {e}\nRaw response: {raw_text}")

# --- FastAPI Endpoints ---

# A simple root endpoint to check if the server is running
@app.get("/")
def read_root():
    return {"status": "API is running"}

# The main endpoint for summarization
@app.get("/summarize")
def get_summary_endpoint(url: str = Query(..., description="YouTube video URL")):
    try:
        video_id = extract_youtube_id(url)
        transcript = get_transcript(video_id)
        summary = summarize_with_gemini(transcript)
        return summary
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})