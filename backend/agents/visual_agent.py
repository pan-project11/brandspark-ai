import json, base64, requests
import google.auth
import google.auth.transport.requests
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from utils.gcs import upload_to_gcs
from typing import AsyncGenerator

class VisualAgent(BaseAgent):
    async def _run_async_impl(self, ctx, **kwargs):
        copy_raw = ctx.session.state.get("copy", "{}")
        copy = json.loads(copy_raw) if isinstance(copy_raw, str) else copy_raw
        strategy_raw = ctx.session.state.get("strategy", "{}")
        strategy = json.loads(strategy_raw) if isinstance(strategy_raw, str) else strategy_raw
        image_prompt = copy.get("image_prompt", "premium product advertisement")
        tagline = copy.get("tagline", "")
        theme_ctx = ctx.session.state.get("theme_context", "")
        color_ctx = ctx.session.state.get("color_context", "")
        image_size = ctx.session.state.get("image_size", "1:1")
        product_analysis = ctx.session.state.get("product_analysis", "")
        campaign_dir = strategy.get("campaign_theme", {}).get("creative_direction", "")
        valid_ratios = {"1:1", "9:16", "16:9", "4:5", "3:4"}
        aspect_ratio = image_size if image_size in valid_ratios else "1:1"
        product_ref = f"Product: {product_analysis}." if product_analysis else ""
        campaign_ref = f"Creative direction: {campaign_dir}." if campaign_dir else ""
        prompts = [
            f"{image_prompt}. {theme_ctx} {color_ctx} {product_ref} {campaign_ref} Cinematic photorealistic premium advertisement photography.",
            f"Social media ad for '{tagline}'. {theme_ctx} {color_ctx} {product_ref} Bold vibrant lifestyle photography highly shareable.",
        ]
        credentials, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        token = credentials.token
        image_urls = []
        for prompt in prompts:
            url = "https://us-central1-aiplatform.googleapis.com/v1/projects/gen-lang-client-0134408223/locations/us-central1/publishers/google/models/imagen-3.0-generate-001:predict"
            payload = {"instances": [{"prompt": prompt}], "parameters": {"sampleCount": 1, "aspectRatio": aspect_ratio}}
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            resp = requests.post(url, json=payload, headers=headers)
            result = resp.json()
            predictions = result.get("predictions", [])
            if not predictions:
                continue
            pred = predictions[0]
            b64 = pred.get("bytesBase64Encoded") or pred.get("b64JsonImage") or pred.get("imageBytes")
            if not b64:
                continue
            img_bytes = base64.b64decode(b64)
            gcs_url = await upload_to_gcs(img_bytes, "image/png", prefix="images")
            image_urls.append(gcs_url)
        ctx.session.state["images"] = image_urls
        yield Event(author=self.name, content=types.Content(role="model", parts=[types.Part(text=json.dumps({"images": image_urls}))]))

visual_agent = VisualAgent(name="visual_agent", description="Generates images via Imagen 3")
