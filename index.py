import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from mangum import Mangum
import json

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()

def extract_youtube_id(url: str) -> str:
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0].split("?")[0]
    elif "youtu.be/" in url:
        return url.split("/")[-1].split("?")[0].split("&")[0]
    else:
        raise ValueError("❌ Invalid YouTube URL")

def get_best_transcript(video_id: str) -> str:
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = None

    try:
        transcript = transcript_list.find_manually_created_transcript(['en'])
    except:
        pass

    if transcript is None:
        try:
            transcript = transcript_list.find_generated_transcript(['en'])
        except:
            pass

    if transcript is None:
        for t in transcript_list:
            if 'en' in [lang['language_code'] for lang in t.translation_languages]:
                transcript = t.translate('en')
                break

    if transcript is None:
        raise Exception("❌ No usable transcript found.")

    entries = transcript.fetch()
    return "\n".join(entry.text for entry in entries)

def summarize_with_gemini(transcript_text: str) -> dict:
    if not GEMINI_API_KEY:
        raise Exception("❌ Gemini API key not set.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-2.5-pro"

    prompt = f"""Return a brief JSON summary:
{{
  "topic_name": "name of topic",
  "topic_summary": "summary of topic"
}}

Transcript:
\"\"\" 
{transcript_text}
\"\"\""""

    contents = [types.Content(role="user", parts=[types.Part.from_text(prompt)])]
    config = types.GenerateContentConfig(
        temperature=0.6,
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
        response_mime_type="text/plain"
    )

    response = client.models.generate_content(
        model=model, contents=contents, config=config
    )

    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        raise Exception(f"❌ Failed to parse Gemini output: {raw_text}")

@app.get("/summarize")
def get_summary(url: str = Query(..., description="YouTube video URL")):
    try:
        video_id = extract_youtube_id(url)
        transcript = get_best_transcript(video_id)
        summary = summarize_with_gemini(transcript)
        return summary
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ✅ Needed for Vercel
handler = Mangum(app)
