import json, os
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google import genai
from google.genai import types
from typing import AsyncGenerator

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

class StrategyAgent(BaseAgent):
    async def _run_async_impl(self, ctx, **kwargs):
        product_desc = ctx.session.state.get("product_description", "")
        language = ctx.session.state.get("language", "English")
        theme = ctx.session.state.get("theme", "")
        brand_colors = ctx.session.state.get("brand_colors", "")
        product_analysis = ctx.session.state.get("product_analysis", "")
        theme_ctx = f"Seasonal theme: {theme}." if theme else ""
        color_ctx = f"Brand colors: {brand_colors}." if brand_colors else ""
        lang_note = f"Write all text in {language}." if language != "English" else ""
        response = await client.aio.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"You are a marketing strategist. Analyze: {product_desc}\n{theme_ctx}{color_ctx}{lang_note}\nReturn ONLY valid JSON with these keys: product_understanding(core_benefit,emotional_hook,category,price_positioning), target_audience(primary,secondary,age_range,gender_skew,psychographics,pain_points,motivations), market_positioning(statement,differentiators,competitor_gaps,brand_archetype), campaign_theme(big_idea,creative_direction,campaign_name), tone_of_voice, marketing_funnel(awareness,consideration,conversion,retention), recommended_channels(channel,priority,reason), budget_split(category,percentage), kpis(metric,target)"
        )
        text = response.text.strip()
        if "```" in text:
            text = text.split("```json")[-1].split("```")[0].strip()
        try:
            strategy = json.loads(text)
        except Exception:
            strategy = {"product_understanding":{"core_benefit":"Quality","emotional_hook":"Pride","category":"Consumer goods","price_positioning":"Premium"},"target_audience":{"primary":"Adults 25-40","secondary":"Gift buyers","age_range":"25-40","gender_skew":"70% female","psychographics":"Quality-focused","pain_points":["Time","Options","Quality"],"motivations":["Self-care","Gifting","Lifestyle"]},"market_positioning":{"statement":"Premium choice for discerning consumers","differentiators":["Curated","Premium","Thoughtful"],"competitor_gaps":"Premium segment gap","brand_archetype":"The Caregiver"},"campaign_theme":{"big_idea":"Experience quality","creative_direction":"Warm aspirational","campaign_name":"Made with Care"},"tone_of_voice":"Warm and empowering","marketing_funnel":{"awareness":"Social + influencer","consideration":"Reviews + UGC","conversion":"Offers + proof","retention":"Loyalty + email"},"recommended_channels":[{"channel":"Instagram","priority":"High","reason":"Visual"},{"channel":"TikTok","priority":"High","reason":"Viral"},{"channel":"Email","priority":"High","reason":"ROI"}],"budget_split":[{"category":"Paid Social","percentage":35},{"category":"Content","percentage":20},{"category":"Influencer","percentage":20},{"category":"Email","percentage":15},{"category":"SEO","percentage":10}],"kpis":[{"metric":"ROAS","target":"3-4x"},{"metric":"CPA","target":"<$20"},{"metric":"CVR","target":">2.5%"}]}
        ctx.session.state["strategy"] = strategy
        yield Event(author=self.name, content=types.Content(role="model", parts=[types.Part(text=json.dumps(strategy))]))

strategy_agent = StrategyAgent(name="strategy_agent", description="Marketing strategy")
