import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import json 

# Load environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# Your original URL extraction function
def extract_youtube_id(url: str) -> str:
    if "watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("/")[-1].split("?")[0]
    else:
        raise ValueError("❌ Invalid YouTube URL")

# Your original transcript function with the corrected API call
def get_best_transcript(video_id: str) -> str:
    # This is the correct way to call the library, without creating an instance
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = None

    try:
        transcript = transcript_list.find_manually_created_transcript(['en'])
        print("✅ Using manually created English transcript.")
    except:
        pass

    if transcript is None:
        try:
            transcript = transcript_list.find_generated_transcript(['en'])
            print("⚠️ Using auto-generated English transcript.")
        except:
            pass

    if transcript is None:
        for t in transcript_list:
            if t.is_translatable:
                try:
                    transcript = t.translate('en')
                    print(f"🌐 Using {t.language_code} transcript and translating to English...")
                    break
                except:
                    continue

    if transcript is None:
        raise Exception("❌ No usable transcript found.")

    entries = transcript.fetch()
    # THE FIX: The library returns a dictionary, so use entry['text']
    full_text = "\n".join(entry['text'] for entry in entries)
    return full_text

# Your original Gemini function, updated to the current stable method
def summarize_with_gemini(transcript_text: str) -> dict:
    if not GEMINI_API_KEY:
        raise Exception("❌ Gemini API key not set in environment.")
    
    # This is the current, reliable way to call the Gemini API
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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

    if raw_text.startswith("```json"):
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(raw_text)
        return parsed
    except json.JSONDecodeError as e:
        raise Exception(f"❌ Failed to parse Gemini response as JSON: {e}\nRaw response: {raw_text}")

# Your original endpoint
@app.get("/summarize")
def get_summary(url: str = Query(..., description="YouTube video URL")):
    try:
        video_id = extract_youtube_id(url)
        transcript_text = get_best_transcript(video_id)
        summary = summarize_with_gemini(transcript_text)
        return summary
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Optional root endpoint for basic testing
@app.get("/")
def read_root():
    return {"status": "API is running"}