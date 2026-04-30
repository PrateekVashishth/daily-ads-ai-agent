"""
agents/video_producer.py
──────────────────────────
Agent 4 – Video Producer

Responsibility:
  Take the 60-second ad script (Agent 3) and produce a complete video
  production brief that can be fed directly into Remotion + ElevenLabs
  (or any free-tier image/video tool).

  Output includes:
    • Scene-by-scene visual direction
    • Voice-over text per scene (ready for ElevenLabs TTS)
    • On-screen text / subtitle copy
    • B-roll / stock image keywords per scene
    • Remotion component structure suggestion
    • ElevenLabs voice settings recommendation
"""

from crewai import Agent
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL


def create_video_producer() -> Agent:
    llm_config = {
        "model": OPENROUTER_MODEL,
        "api_key": OPENROUTER_API_KEY,
        "base_url": OPENROUTER_BASE_URL,
    }

    return Agent(
        role="Video Production Director",
        goal=(
            "Transform the 60-second ad script into a complete, production-ready "
            "video brief including scene-by-scene directions, voice-over text, "
            "subtitle copy, stock image search keywords, and a Remotion "
            "component structure with ElevenLabs voice settings."
        ),
        backstory=(
            "You are a creative director and motion-design producer who has made "
            "hundreds of short-form performance ads. You think visually: every line "
            "of the script maps to a concrete visual scene. You are fluent in "
            "Remotion (React-based video rendering) and know how to pair voice "
            "pacing (via ElevenLabs) with text overlays for maximum retention. "
            "Your briefs are detailed enough that a developer can implement them "
            "immediately without further clarification."
        ),
        tools=[],
        llm=llm_config,
        verbose=True,
        max_iter=2,
        memory=False,
    )
