from http.server import BaseHTTPRequestHandler
import json
import asyncio

FALLBACK = [
    {"id": "ur-PK-AsadNeural", "name": "Asad (Male)", "gender": "Male", "locale": "ur-PK"},
    {"id": "ur-PK-AyeshaNeural", "name": "Ayesha (Female)", "gender": "Female", "locale": "ur-PK"},
]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            import edge_tts

            async def get():
                vs = await edge_tts.list_voices()
                out = []
                for v in vs:
                    if str(v.get("Locale", "")).startswith("ur"):
                        out.append({
                            "id": v["ShortName"],
                            "name": v.get("FriendlyName", v["ShortName"]),
                            "gender": v.get("Gender"),
                            "locale": v["Locale"],
                        })
                return out or FALLBACK

            voices = asyncio.run(get())
        except Exception:
            voices = FALLBACK
        body = json.dumps({"voices": voices}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
