"""
agents/ad_researcher.py
────────────────────────
Agent 1 – Ad Researcher

Responsibility:
  Search Meta Ads Library for successful ads in the CrowdWisdomTrading
  niche, select the top-performing ads from the last 30 days, and save
  them as a structured JSON file for downstream agents.
"""

from crewai import Agent
from tools.apify_tool import ApifyMetaAdsTool
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL


def create_ad_researcher() -> Agent:
    llm_config = {
        "model": OPENROUTER_MODEL,
        "api_key": OPENROUTER_API_KEY,
        "base_url": OPENROUTER_BASE_URL,
    }

    return Agent(
        role="Meta Ads Research Specialist",
        goal=(
            "Search the Meta Ads Library for the most effective ads related to "
            "CrowdWisdomTrading and the trading signals niche. "
            "Identify and return the top 20 best-performing, currently active ads "
            "from the last 30 days."
        ),
        backstory=(
            "You are a seasoned paid-media analyst with deep expertise in Facebook and "
            "Instagram advertising for financial services. You know exactly what makes "
            "an ad 'work' – strong hooks, clear value propositions, social proof, and "
            "compelling CTAs. You use data to identify patterns rather than relying on gut feel."
        ),
        tools=[ApifyMetaAdsTool()],
        llm=llm_config,
        verbose=True,
        max_iter=3,
        memory=False,
    )
