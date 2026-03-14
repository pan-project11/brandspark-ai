import json, os
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google import genai
from google.genai import types
from typing import AsyncGenerator

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

class SocialAgent(BaseAgent):
    async def _run_async_impl(self, ctx, **kwargs):
        copy_raw = ctx.session.state.get("copy", "{}")
        copy = json.loads(copy_raw) if isinstance(copy_raw, str) else copy_raw
        product_desc = ctx.session.state.get("product_description", "")
        language = ctx.session.state.get("language", "English")
        lang_instruction = f"IMPORTANT: Write ALL social media posts in {language} only. Do not use English at all." if language != "English" else ""
        response = await client.aio.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"""You are a social media expert.
{lang_instruction}
Product: {product_desc}
Tagline: {copy.get('tagline','')}
Return ONLY valid JSON, no markdown:
{{"instagram":"caption with emojis in {language}","twitter":"tweet under 280 chars in {language}","linkedin":"professional post in {language}","hashtags":["tag1","tag2","tag3","tag4","tag5"]}}"""
        )
        text = response.text.strip()
        if "```" in text:
            text = text.split("```json")[-1].split("```")[0].strip()
        try:
            social = json.loads(text)
        except Exception:
            social = {"instagram":f"✨ {copy.get('tagline','')} ✨","twitter":f"{copy.get('tagline','')}","linkedin":f"{copy.get('hero_copy','')}","hashtags":["marketing","brand","campaign","digital","creative"]}
        ctx.session.state["social"] = social
        yield Event(author=self.name, content=types.Content(role="model", parts=[types.Part(text=json.dumps(social))]))

social_agent = SocialAgent(name="social_agent", description="Generates social media posts")
