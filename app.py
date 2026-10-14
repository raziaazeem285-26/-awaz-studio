"""AwazStudio — free Urdu text-to-speech studio (FastAPI, Vercel-ready).

Routes:
  GET  /            -> studio UI (index.html)
  GET  /api/voices  -> Urdu voices list (JSON)
  POST /api/tts     -> {text, voice, rate} -> MP3 audio
"""
import asyncio
import os
import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response

app = FastAPI(title="AwazStudio")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FALLBACK_VOICES = [
    {"id": "ur-PK-AsadNeural", "name": "Asad (Male)", "gender": "Male", "locale": "ur-PK"},
    {"id": "ur-PK-AyeshaNeural", "name": "Ayesha (Female)", "gender": "Female", "locale": "ur-PK"},
]

MAX_CHARS = 2000


@app.get("/api/voices")
async def list_voices():
    """Urdu voices ki live list (Edge TTS se)."""
    try:
        import edge_tts

        raw = await edge_tts.list_voices()
        out = []
        for v in raw:
            if str(v.get("Locale", "")).startswith("ur"):
                out.append(
                    {
                        "id": v["ShortName"],
                        "name": v.get("FriendlyName", v["ShortName"]),
                        "gender": v.get("Gender"),
                        "locale": v["Locale"],
                    }
                )
        return {"voices": out or FALLBACK_VOICES}
    except Exception:
        return {"voices": FALLBACK_VOICES}


@app.post("/api/tts")
async def make_speech(payload: dict):
    """Text -> MP3. Body: {"text": "...", "voice": "ur-PK-...", "rate": "+0%"}"""
    text = str(payload.get("text", "")).strip()
    voice = str(payload.get("voice", "")).strip()
    rate = str(payload.get("rate", "+0%")).strip() or "+0%"

    if not (1 <= len(text) <= MAX_CHARS):
        raise HTTPException(status_code=400, detail=f"Text 1-{MAX_CHARS} characters hona chahiye")
    if not voice.startswith("ur"):
        raise HTTPException(status_code=400, detail="Sirf Urdu voices allowed hain")
    if not re.fullmatch(r"[+-]\d{1,3}%", rate):
        raise HTTPException(status_code=400, detail="Rate format ghalat hai")

    tmp = "/tmp/awazstudio_out.mp3"
    try:
        import edge_tts

        comm = edge_tts.Communicate(text, voice, rate=rate)
        await comm.save(tmp)
        with open(tmp, "rb") as f:
            data = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Awaz nahi ban saki: {e}")
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass

    return Response(
        content=data,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": 'attachment; filename="awazstudio.mp3"',
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.get("/")
async def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"), media_type="text/html")


@app.get("/health")
async def health():
    return JSONResponse({"ok": True, "service": "awaz-studio"})
