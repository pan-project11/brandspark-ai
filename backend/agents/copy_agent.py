import json
import os
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google import genai
from google.genai import types
from typing import AsyncGenerator

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

class CopyAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        product_desc = ctx.session.state.get("product_description", "")

        response = await client.aio.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"""You are a creative advertising copywriter.
Create marketing copy for: {product_desc}

Respond with ONLY a JSON object, no markdown, no explanation:
{{"tagline": "short catchy tagline", "hero_copy": "2-3 sentence compelling description", "headlines": ["headline 1", "headline 2", "headline 3"], "image_prompt": "detailed visual prompt for an advertisement image"}}"""
        )

        text = response.text.strip()
        # Strip markdown if present
        if "```" in text:
            text = text.split("```json")[-1].split("```")[0].strip()
        if text.startswith("```"):
            text = text.strip("```").strip()

        try:
            copy = json.loads(text)
        except Exception:
            # Fallback if JSON parsing fails
            copy = {
                "tagline": "Stay Hydrated, Stay Glowing",
                "hero_copy": f"Introducing the smart way to hydrate. {product_desc}",
                "headlines": ["Never Forget to Drink Again", "Hydration Meets Innovation", "Glow Your Way to Health"],
                "image_prompt": f"Premium lifestyle product advertisement for {product_desc}, cinematic lighting"
            }

        ctx.session.state["copy"] = copy

        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part(text=json.dumps(copy))]
            )
        )

copy_agent = CopyAgent(
    name="copy_agent",
    description="Generates marketing copy"
)
