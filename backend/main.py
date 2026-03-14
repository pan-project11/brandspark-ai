import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BrandSpark AI API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class CampaignRequest(BaseModel):
    description: str
    language: Optional[str] = "English"
    theme: Optional[str] = ""
    brand_colors: Optional[str] = ""
    image_size: Optional[str] = "1:1"
    product_images: Optional[List[str]] = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
async def generate(req: CampaignRequest):
    if len(req.description) < 10:
        raise HTTPException(400, "Description too short")
    from utils.stream import campaign_stream
    return StreamingResponse(
        campaign_stream(
            product_description=req.description,
            language=req.language,
            theme=req.theme,
            brand_colors=req.brand_colors,
            image_size=req.image_size,
            product_images=req.product_images
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
