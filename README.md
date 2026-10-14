# AwazStudio — Free Urdu Text to Speech

A tiny web studio (mini ElevenLabs) for natural Urdu voiceovers:
paste text → pick a male/female Urdu voice → download MP3.
Built for Razia's YouTube & social media voiceovers; free for anyone.

**Live:** https://awaz-studio.vercel.app/ (after deploy)

## How it works

- `index.html` — single-page studio UI (golden #D4AF37 + dark blue #0A1A33, Poppins).
- `app.py` — FastAPI app (Vercel Python runtime auto-detects it):
  - `GET /` serves the studio UI
  - `GET /api/voices` lists Urdu voices live via `edge_tts.list_voices()`
    (Locale starting with `ur`); falls back to `ur-PK-AsadNeural` (Male)
    and `ur-PK-AyeshaNeural` (Female) if the live query fails
  - `POST /api/tts` with `{text, voice, rate}` → MP3 audio (`audio/mpeg`).
    Max 2000 chars per request, voice must start with `ur`, rate like `+0%`
- `requirements.txt` — `fastapi` + `edge-tts` (no API keys needed)

## Deploy (Vercel)

1. Create an empty **public** repo named `awaz-studio` on GitHub.
2. Push these files to `main`.
3. Vercel → Add New Project → Import `awaz-studio` → Framework Preset: **Other** → Deploy.
4. Every push to `main` auto-deploys.

## Limits (current, free tier)

- 2000 characters per request (split long scripts into parts).
- Serverless function timeout 60s (`vercel.json`).
- Voices come from Microsoft Edge TTS (free, no key). If Microsoft changes
  voice availability, `/api/voices` falls back to the two hardcoded Urdu voices.

## Monetize later (notes, not implemented)

- Accounts: Vercel + a tiny DB (e.g. Vercel KV / Supabase) for per-user quotas.
- Quotas: free X chars/day, paid plans for more (track usage per account in the DB).
- Payments: Stripe Checkout for subscriptions; gate `/api/tts` behind the quota check.
- Keep the free tier generous to keep attracting visitors; charge power users.
