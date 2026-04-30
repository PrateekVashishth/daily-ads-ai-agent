"""
agents/script_writer.py
─────────────────────────
Agent 3 – Ad Script Writer

Responsibility:
  Use the marketing analysis (Agent 2) AND the brand data from Google Drive
  to write a compelling, platform-native 60-second video ad script.
  The script must be grounded in real data and follow a proven structure.
"""

from crewai import Agent
from tools.gdrive_tool import GDriveBrandDataTool
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL


def create_script_writer() -> Agent:
    llm_config = {
        "model": OPENROUTER_MODEL,
        "api_key": OPENROUTER_API_KEY,
        "base_url": OPENROUTER_BASE_URL,
    }

    return Agent(
        role="Video Ad Script Writer",
        goal=(
            "Write a high-converting 60-second video ad script for CrowdWisdomTrading "
            "that is grounded in the identified pain points, uses real brand data "
            "(USPs, testimonials, pricing) from Google Drive, and follows a proven "
            "hook → agitate → solution → proof → CTA structure."
        ),
        backstory=(
            "You are an award-winning short-form video copywriter who specialises in "
            "direct-response ads for fintech and trading platforms. You craft every "
            "script with a single goal: make the viewer stop scrolling and take action. "
            "You know that the first 3 seconds determine everything, and you never waste "
            "a single word. You also ensure every claim is backed by the brand's own data."
        ),
        tools=[GDriveBrandDataTool()],
        llm=llm_config,
        verbose=True,
        max_iter=2,
        memory=False,
    )
