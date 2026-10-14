from http.server import BaseHTTPRequestHandler
import json
import asyncio
import os
import re

MAX_CHARS = 2000
RATE_RE = re.compile(r"^[+-]\d{1,3}%$")
OUT_PATH = "/tmp/awazstudio_out.mp3"


class handler(BaseHTTPRequestHandler):
    def _send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        text = str(payload.get("text", "")).strip()
        voice = str(payload.get("voice", ""))
        rate = str(payload.get("rate", "+0%"))

        if not (1 <= len(text) <= MAX_CHARS):
            self._send_json(400, {"error": f"text must be 1..{MAX_CHARS} characters"})
            return
        if not voice.startswith("ur"):
            self._send_json(400, {"error": "voice must be an Urdu voice"})
            return
        if not RATE_RE.match(rate):
            self._send_json(400, {"error": "rate must look like +0% / -25% / +50%"})
            return

        try:
            import edge_tts

            async def run():
                comm = edge_tts.Communicate(text, voice, rate=rate)
                await comm.save(OUT_PATH)

            asyncio.run(run())
            with open(OUT_PATH, "rb") as f:
                data = f.read()
        except Exception as e:
            self._send_json(500, {"error": "TTS failed: " + str(e)[:200]})
            return
        finally:
            try:
                if os.path.exists(OUT_PATH):
                    os.remove(OUT_PATH)
            except Exception:
                pass

        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Disposition", 'attachment; filename="awazstudio.mp3"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
