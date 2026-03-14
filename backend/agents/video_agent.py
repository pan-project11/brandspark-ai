import json
import os
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google.cloud import texttospeech
from google import genai
from google.genai import types
from utils.gcs import upload_to_gcs
from typing import AsyncGenerator

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

class VideoAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        copy_raw = ctx.session.state.get("copy", "{}")
        copy = json.loads(copy_raw) if isinstance(copy_raw, str) else copy_raw
        product_desc = ctx.session.state.get("product_description", "")

        response = await client.aio.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"""Write a 15-second video ad script for: {product_desc}
Hero copy: {copy.get('hero_copy', '')}
Return valid JSON only:
{{
  "scenes": [
    {{"scene": "desc", "vo": "voiceover text", "duration": 5}},
    {{"scene": "desc", "vo": "voiceover text", "duration": 5}},
    {{"scene": "desc", "vo": "voiceover text", "duration": 5}}
  ],
  "full_vo": "complete voiceover paragraph"
}}"""
        )

        text = response.text.strip()
        if "```" in text:
            text = text.split("```json")[-1].split("```")[0].strip()
        script_data = json.loads(text)

        tts = texttospeech.TextToSpeechClient()
        tts_resp = tts.synthesize_speech(
            input=texttospeech.SynthesisInput(text=script_data["full_vo"]),
            voice=texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Journey-F"
            ),
            audio_config=texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.1
            )
        )
        audio_url = await upload_to_gcs(
            tts_resp.audio_content, "audio/mpeg", prefix="audio"
        )
        result = {"script": script_data, "voiceover_url": audio_url}
        ctx.session.state["video"] = result

        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part(text=json.dumps(result))]
            )
        )

video_agent = VideoAgent(
    name="video_agent",
    description="Script + TTS voiceover"
)
