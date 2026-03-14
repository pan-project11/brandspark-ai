import json, asyncio, base64, os
from typing import AsyncGenerator, List
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.orchestrator import root_agent

THEME_STYLES = {
    "Christmas": "festive red and green, Christmas trees, snow, cozy warmth, gift-giving",
    "Hari Raya": "Eid Mubarak, ketupat, Malay lanterns, gold and green, family togetherness",
    "Diwali": "Festival of Lights, diyas, vibrant colors, gold, rangoli, prosperity",
    "Chinese New Year": "Lunar New Year, red envelopes, lanterns, gold and red, abundance",
    "Holi": "Festival of Colors, powder colors, joy, spring, playful energy",
    "Black Friday": "massive sale, bold black and red, urgency, limited time deals",
    "Valentine's Day": "romance, roses, hearts, love, pink and red palette",
    "Mother's Day": "celebrating mothers, floral, soft pastels, warmth, appreciation",
    "Halloween": "spooky fun, orange and black, pumpkins, playful horror",
    "Thanksgiving": "gratitude, harvest, warm autumn colors, family gathering",
    "Ramadan": "spiritual, crescent moon, stars, gold and purple, community",
    "New Year": "celebration, fireworks, gold and silver, new beginnings"
}

async def analyze_product_images(images_b64, api_key):
    if not images_b64:
        return ""
    try:
        from google import genai as gc
        client = gc.Client(api_key=api_key)
        parts = [types.Part(text="Analyze these product images for marketing. Describe colors, style, materials, mood, target appeal, and visual elements for advertising:")]
        for img_b64 in images_b64[:3]:
            raw = img_b64.split(",")[1] if "," in img_b64 else img_b64
            try:
                img_bytes = base64.b64decode(raw)
                parts.append(types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=img_bytes)))
            except Exception:
                continue
        resp = await client.aio.models.generate_content(model="gemini-3-flash-preview", contents=parts)
        return resp.text.strip()
    except Exception:
        return ""

async def campaign_stream(
    product_description: str,
    language: str = "English",
    theme: str = "",
    brand_colors: str = "",
    image_size: str = "1:1",
    product_images: List[str] = []
) -> AsyncGenerator[str, None]:

    def evt(type_, key, content):
        return f"data: {json.dumps({'type': type_, 'key': key, 'content': content})}\n\n"

    try:
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        product_analysis = ""
        if product_images:
            yield evt("status", "analyzing", "Analyzing your product images...")
            product_analysis = await analyze_product_images(product_images, api_key)

        theme_context = f"Visual theme: {theme}. Style: {THEME_STYLES.get(theme, theme)}." if theme else ""
        color_context = f"Use these brand colors prominently: {brand_colors}." if brand_colors else ""
        lang_context = f"Generate ALL text in {language}. Do not mix languages." if language != "English" else ""

        session_service = InMemorySessionService()
        runner = Runner(agent=root_agent, app_name="brandspark", session_service=session_service)

        session = await session_service.create_session(
            app_name="brandspark",
            user_id="user",
            state={
                "product_description": product_description,
                "language": language,
                "theme": theme,
                "brand_colors": brand_colors,
                "image_size": image_size,
                "theme_context": theme_context,
                "color_context": color_context,
                "lang_context": lang_context,
                "product_analysis": product_analysis,
            }
        )

        yield evt("status", "thinking", "Briefing your creative team...")

        full_message = "\n".join(filter(None, [
            product_description, theme_context, color_context, lang_context,
            f"Product visual reference: {product_analysis}" if product_analysis else ""
        ]))

        message = types.Content(role="user", parts=[types.Part(text=full_message)])
        results = {}

        async for event in runner.run_async(user_id="user", session_id=session.id, new_message=message):
            if not hasattr(event, 'author') or not event.content or not event.content.parts:
                continue
            try:
                text = event.content.parts[0].text
                if not text:
                    continue
                data = json.loads(text)
                results[event.author] = data
                status_map = {
                    "strategy_agent": ("strategy_done", "Strategy complete!"),
                    "copy_agent": ("copy_done", "Copy written!"),
                    "visual_agent": ("images_done", "Visuals generated!"),
                    "video_agent": ("video_done", "Voiceover ready!"),
                    "social_agent": ("social_done", "Social posts ready!"),
                }
                if event.author in status_map:
                    key, msg = status_map[event.author]
                    yield evt("status", key, msg)
            except Exception:
                continue

        strategy = results.get("strategy_agent", {})
        copy     = results.get("copy_agent", {})
        visual   = results.get("visual_agent", {})
        video    = results.get("video_agent", {})
        social   = results.get("social_agent", {})
        images   = visual.get("images", [])

        if strategy:
            yield evt("json", "strategy", strategy)
            await asyncio.sleep(0.05)
        if copy.get("tagline"):
            yield evt("text", "tagline", copy["tagline"])
            await asyncio.sleep(0.05)
        if copy.get("hero_copy"):
            yield evt("text", "hero_copy", copy["hero_copy"])
            await asyncio.sleep(0.05)
        if copy.get("headlines"):
            yield evt("text", "headlines", copy["headlines"])
            await asyncio.sleep(0.05)
        if images:
            yield evt("image", "hero_image", images[0])
            await asyncio.sleep(0.05)
        if video.get("script"):
            yield evt("text", "script", video["script"])
            await asyncio.sleep(0.05)
        if video.get("voiceover_url"):
            yield evt("audio", "voiceover", video["voiceover_url"])
            await asyncio.sleep(0.05)
        if len(images) > 1:
            yield evt("image", "social_image", images[1])
            await asyncio.sleep(0.05)
        if social:
            yield evt("text", "social", social)
        yield 'data: {"type":"done"}\n\n'

    except Exception as e:
        import traceback
        yield f"data: {json.dumps({'type': 'error', 'content': str(e) + ' | ' + traceback.format_exc()})}\n\n"
