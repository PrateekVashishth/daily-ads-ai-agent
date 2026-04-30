"""
tasks/task_definitions.py
──────────────────────────
Defines the four CrewAI tasks, one per agent.
Each task has a clear expected_output so the crew knows when it is done.
"""

import json
from pathlib import Path

from crewai import Task

from config.settings import OUTPUT_DIR, TARGET_NICHE, TARGET_URL


# ─────────────────────────────────────────────────────────────────────────────
# Task 1 – Search & select top ads
# ─────────────────────────────────────────────────────────────────────────────

def create_research_task(agent) -> Task:
    return Task(
        description=(
            f"Use the Meta Ads Library Scraper tool to search for active ads "
            f"related to the niche '{TARGET_NICHE}' and the website '{TARGET_URL}'. "
            f"Focus on the last 30 days. "
            f"Select up to 20 of the best-performing ads (prefer video ads, longer copy, "
            f"and ads that are still running). "
            f"Return the results as a well-formed JSON array. "
            f"Also save the JSON to: {OUTPUT_DIR}/raw_ads.json"
        ),
        expected_output=(
            "A JSON array of up to 20 ads, each with fields: "
            "ad_id, page_name, body, headline, cta, start_date, "
            "has_video, image_urls, video_url, ad_url, platforms."
        ),
        agent=agent,
        output_file=str(OUTPUT_DIR / "raw_ads.json"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Task 2 – Extract marketing intelligence
# ─────────────────────────────────────────────────────────────────────────────

def create_analysis_task(agent, research_task: Task) -> Task:
    return Task(
        description=(
            "You will receive a JSON list of top-performing Meta ads (from the previous task). "
            "Analyse all ads carefully and extract:\n"
            "  1. TOP_PAIN_POINTS – the 5 most frequently addressed customer pain points\n"
            "  2. WINNING_HOOKS – the 5 strongest opening hooks / first lines\n"
            "  3. MARKETING_ANGLES – the 3 dominant value angles (e.g. speed, accuracy, community)\n"
            "  4. PROOF_PATTERNS – types of social proof used (numbers, testimonials, guarantees)\n"
            "  5. CTA_PATTERNS – most effective calls-to-action\n"
            "  6. EMOTIONAL_TRIGGERS – key emotions leveraged (fear of missing out, greed, frustration)\n"
            "  7. AD_STRUCTURE – the most common structural pattern across top ads\n\n"
            "Return a single, clean JSON object with these 7 keys. "
            f"Also save to: {OUTPUT_DIR}/marketing_analysis.json"
        ),
        expected_output=(
            "A JSON object with 7 keys: TOP_PAIN_POINTS, WINNING_HOOKS, MARKETING_ANGLES, "
            "PROOF_PATTERNS, CTA_PATTERNS, EMOTIONAL_TRIGGERS, AD_STRUCTURE. "
            "Each key maps to a list of concise, actionable strings."
        ),
        agent=agent,
        context=[research_task],
        output_file=str(OUTPUT_DIR / "marketing_analysis.json"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Task 3 – Write the 60-second ad script
# ─────────────────────────────────────────────────────────────────────────────

def create_script_task(agent, analysis_task: Task) -> Task:
    return Task(
        description=(
            "Using the marketing analysis from the previous task AND the brand data "
            "from Google Drive (use the GDrive tool to fetch it), write a compelling "
            "60-second video ad script for CrowdWisdomTrading.\n\n"
            "The script MUST:\n"
            "  • Open with one of the WINNING_HOOKS identified in the analysis\n"
            "  • Address the #1 TOP_PAIN_POINT within the first 5 seconds\n"
            "  • Introduce CrowdWisdomTrading as the unique solution by second 15\n"
            "  • Include at least 2 specific proof points (real stats, testimonial snippets)\n"
            "  • Naturally weave in a USP from the brand data\n"
            "  • End with a clear, time-pressured CTA by second 55\n"
            "  • Be written in a conversational tone suitable for Facebook/Instagram Reels\n\n"
            "Format the output as a JSON object with keys:\n"
            "  script_title, hook (0-3s), pain_agitation (3-15s), solution (15-30s), "
            "proof (30-45s), offer (45-55s), cta (55-60s), full_script_text\n\n"
            f"Save to: {OUTPUT_DIR}/ad_script.json"
        ),
        expected_output=(
            "A JSON object with the complete 60-second ad script broken into timed sections: "
            "hook, pain_agitation, solution, proof, offer, cta, and full_script_text."
        ),
        agent=agent,
        context=[analysis_task],
        output_file=str(OUTPUT_DIR / "ad_script.json"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Task 4 – Video production brief
# ─────────────────────────────────────────────────────────────────────────────

def create_video_task(agent, script_task: Task) -> Task:
    return Task(
        description=(
            "Take the 60-second ad script from the previous task and produce a "
            "complete video production brief for Remotion + ElevenLabs.\n\n"
            "The brief MUST include:\n\n"
            "SCENES (array of 6-8 scenes):\n"
            "  Each scene: { scene_number, duration_seconds, visual_description, "
            "  voiceover_text, on_screen_text, subtitle_text, stock_keywords }\n\n"
            "REMOTION_CONFIG:\n"
            "  { fps, width, height, durationInFrames, compositionName, "
            "  font_family, color_palette, animation_style }\n\n"
            "ELEVENLABS_CONFIG:\n"
            "  { voice_id, voice_name, stability, similarity_boost, style, "
            "  speaking_rate, rationale }\n\n"
            "STOCK_ASSETS:\n"
            "  A list of 10 specific search queries to find free stock images/videos "
            "  (use Pexels/Unsplash/Pixabay keyword format)\n\n"
            "Return as a single JSON object. "
            f"Save to: {OUTPUT_DIR}/video_brief.json"
        ),
        expected_output=(
            "A JSON production brief with SCENES (array), REMOTION_CONFIG, "
            "ELEVENLABS_CONFIG, and STOCK_ASSETS sections. "
            "Each scene has: scene_number, duration_seconds, visual_description, "
            "voiceover_text, on_screen_text, subtitle_text, stock_keywords."
        ),
        agent=agent,
        context=[script_task],
        output_file=str(OUTPUT_DIR / "video_brief.json"),
    )
