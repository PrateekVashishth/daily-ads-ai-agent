"""
agents/marketing_analyst.py
─────────────────────────────
Agent 2 – Marketing Analyst

Responsibility:
  Analyse the top ads found by Agent 1.
  Extract recurring pain points, marketing angles, hooks, and persuasion
  concepts. Output a structured analysis JSON that Agent 3 will use to
  write a new, evidence-backed ad script.
"""

from crewai import Agent
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL


def create_marketing_analyst() -> Agent:
    llm_config = {
        "model": OPENROUTER_MODEL,
        "api_key": OPENROUTER_API_KEY,
        "base_url": OPENROUTER_BASE_URL,
    }

    return Agent(
        role="Marketing & Copy Strategist",
        goal=(
            "Analyse the top-performing Meta ads and extract the core marketing "
            "intelligence: dominant pain points, emotional hooks, unique angles, "
            "social proof patterns, and CTAs that the market responds to best."
        ),
        backstory=(
            "You are a direct-response copywriter and conversion strategist who has "
            "studied thousands of winning ads across financial services and trading. "
            "You understand consumer psychology, the 'job to be done', and how to "
            "translate data signals into actionable creative strategy. "
            "You communicate findings as crisp, structured JSON that engineers "
            "and creatives can both use."
        ),
        tools=[],          # purely LLM-based analysis; no external tools needed
        llm=llm_config,
        verbose=True,
        max_iter=2,
        memory=False,
    )
