# BrandSpark AI — Full AI Marketing Campaign Generator

🌐 **Live Demo:** https://brandspark-ai-studio.netlify.app

## What is BrandSpark AI?

BrandSpark AI is a full-stack AI-powered marketing campaign generator. Describe any product or service and receive a complete marketing campaign in seconds — including strategy, copy, visuals, video script, voiceover and social media posts.

## Features

- 📊 **Deep Marketing Strategy** — target audience, positioning, funnel, budget split, KPIs
- ✍️ **Campaign Copy** — tagline, hero copy, 3 ad headlines
- 🖼️ **AI-Generated Visuals** — 2 campaign images via Imagen 3
- 🎬 **Video Ad Script** — 3-scene cinematic script
- 🎙️ **Voiceover Audio** — professional TTS narration
- 📱 **Social Media Posts** — Instagram, Twitter/X, LinkedIn + hashtags
- 🌐 **15 Languages** — English, Bahasa Melayu, Mandarin, Hindi, French, Spanish, Arabic, Russian, Japanese, Korean, Portuguese, German, Italian, Thai, Indonesian
- 🎨 **Brand Colors** — 3-color picker incorporated into visuals
- 🎉 **13 Seasonal Themes** — Christmas, Hari Raya, CNY, Diwali, Ramadan, Black Friday and more
- 📐 **5 Image Formats** — Square, Story, Landscape, Portrait
- 🖼️ **Product Image Upload** — upload or URL, analyzed by AI to inform visuals
- ⬇️ **Download Images** — download all generated visuals

## Tech Stack

- **Backend:** Python, FastAPI, Google ADK (Agent Development Kit)
- **AI Agents:** SequentialAgent with 5 sub-agents (Strategy, Copy, Visual, Video, Social)
- **Image Generation:** Imagen 3 via Vertex AI
- **Text Generation:** Gemini 3 Flash
- **Text-to-Speech:** Google Cloud TTS (Journey-F voice)
- **Storage:** Google Cloud Storage
- **Hosting:** Cloud Run (backend) + Netlify (frontend)
- **Streaming:** Server-Sent Events (SSE)

## Architecture
```
User Input
    │
    ▼
FastAPI Backend (Cloud Run)
    │
    ▼
ADK SequentialAgent
    ├── StrategyAgent   → Marketing strategy JSON
    ├── CopyAgent       → Tagline, hero copy, headlines
    ├── VisualAgent     → 2 images via Imagen 3
    ├── VideoAgent      → Script + TTS voiceover
    └── SocialAgent     → Instagram, Twitter, LinkedIn posts
    │
    ▼
SSE Stream → Frontend (Netlify)
```

## How to Test (Reproducible Testing)

### Option 1 — Use the Live App (Easiest)
1. Go to **https://brandspark-ai-studio.netlify.app**
2. Type a product description e.g. `A luxury skincare set with vitamin C serum, moisturizer and eye cream for women aged 30+`
3. Select your language (try Bahasa Melayu or Mandarin!)
4. Pick an image format
5. Set brand colors (optional)
6. Select a seasonal theme e.g. Mother's Day
7. Upload a product image or paste an image URL (optional)
8. Click **Generate Full Campaign**
9. Wait ~60 seconds for the full campaign to stream in
10. Review Strategy, Copy, Images, Script, Voiceover and Social posts
11. Download images using the Download button
12. Copy social posts using the Copy button

### Option 2 — Test the API Directly
```bash
curl -X POST https://pitchforge-backend-632605595642.us-central1.run.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A luxury skincare set for women aged 30+",
    "language": "English",
    "theme": "Mother'"'"'s Day",
    "brand_colors": "#D4447A, #6B3060, #F0A0C0",
    "image_size": "1:1",
    "product_images": []
  }' \
  --no-buffer
```

### Option 3 — Run Locally

**Prerequisites:**
- Python 3.11+
- Google Cloud account with billing enabled
- Gemini API key from https://aistudio.google.com/app/apikey

**Setup:**
```bash
git clone https://github.com/pan-project11/brandspark-ai.git
cd brandspark-ai/backend

pip install -r requirements.txt

export GOOGLE_API_KEY=your_gemini_api_key
export GOOGLE_CLOUD_PROJECT=your_gcp_project_id
export GCS_BUCKET=your_gcs_bucket_name
export GOOGLE_CLOUD_REGION=us-central1

uvicorn main:app --host 0.0.0.0 --port 8080
```

**Then open `frontend/index.html` in your browser** and update the `API` variable to `http://localhost:8080`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/generate` | Generate full campaign (SSE stream) |

### POST /generate Request Body
```json
{
  "description": "Product description (required)",
  "language": "English",
  "theme": "Mother's Day",
  "brand_colors": "#D4447A, #6B3060, #F0A0C0",
  "image_size": "1:1",
  "product_images": ["base64_or_url"]
}
```

## Google Cloud Services Used

1. **Cloud Run** — Backend API hosting
2. **Vertex AI / Imagen 3** — Image generation
3. **Cloud Text-to-Speech** — Voiceover generation
4. **Cloud Storage (GCS)** — Generated asset storage
5. **Cloud Build** — Container builds

## Project Structure
```
brandspark-ai/
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py    # ADK SequentialAgent
│   │   ├── strategy_agent.py  # Marketing strategy
│   │   ├── copy_agent.py      # Campaign copy
│   │   ├── visual_agent.py    # Image generation
│   │   ├── video_agent.py     # Script + TTS
│   │   └── social_agent.py    # Social media posts
│   ├── utils/
│   │   ├── stream.py          # SSE streaming
│   │   └── gcs.py             # GCS upload
│   ├── main.py                # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    └── index.html             # Single-file frontend
```

## Sample Output

Input: `A luxury pregnancy gift box with 12 essentials for expecting mothers`

- **Tagline:** "Twelve moments of pure indulgence."
- **Campaign Name:** "Her First Glow"
- **Target Audience:** Partners aged 25-45 seeking meaningful gifts
- **Channels:** Instagram, Influencer Marketing, Google Search
- **ROAS Target:** 4.0x

## License

MIT License — free to use and modify.
