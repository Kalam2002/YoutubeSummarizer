import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai import types
from mangum import Mangum  # 🔥 Required for Vercel deployment

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

app = FastAPI()

def extract_youtube_id(url: str) -> str:
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0].split("?")[0]
    elif "youtu.be/" in url:
        return url.split("/")[-1].split("?")[0].split("&")[0]
    else:
        raise ValueError("❌ Invalid YouTube URL")

def get_best_transcript(video_id: str) -> str:
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
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
            if 'en' in [lang['language_code'] for lang in t.translation_languages]:
                print(f"🌐 Using {t.language_code} transcript and translating to English...")
                transcript = t.translate('en')
                break

    if transcript is None:
        raise Exception("❌ No usable transcript found.")

    entries = transcript.fetch()
    full_text = "\n".join(entry.text for entry in entries)
    return full_text

def summarize_with_gemini(transcript_text: str) -> dict:
    if not GEMINI_API_KEY:
        raise Exception("❌ Gemini API key not set in environment.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-2.5-pro"

    prompt = f"""Based on the following YouTube transcript, return a brief summary in this JSON format only:
{{
  "topic_name": "name of topic",
  "topic_summary": "summary of topic"
}}

Transcript:
\"\"\" 
{transcript_text}
\"\"\""""

    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    ]

    config = types.GenerateContentConfig(
        temperature=0.6,
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
        response_mime_type="text/plain",
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(raw_text)
        return parsed
    except json.JSONDecodeError as e:
        raise Exception(f"❌ Failed to parse Gemini response as JSON: {e}\nRaw response: {raw_text}")

@app.get("/summarize")
def get_summary(url: str = Query(..., description="YouTube video URL")):
    try:
        video_id = extract_youtube_id(url)
        transcript_text = get_best_transcript(video_id)
        summary = summarize_with_gemini(transcript_text)
        return summary
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ✅ Required for Vercel
handler = Mangum(app)
