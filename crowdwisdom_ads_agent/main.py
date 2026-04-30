"""
main.py
────────
Entry point for the CrowdWisdomTrading Daily Ads AI Agent pipeline.

Pipeline flow:
  Agent 1 (Ad Researcher)      → scrape & select top Meta ads via Apify
  Agent 2 (Marketing Analyst)  → extract pain points, hooks, angles
  Agent 3 (Script Writer)      → write 60-second ad script using brand data
  Agent 4 (Video Producer)     → produce Remotion + ElevenLabs brief

Usage:
  cp .env.example .env          # fill in your API keys
  pip install -r requirements.txt
  python main.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

from crewai import Crew, Process
from loguru import logger

from config.settings import LOGS_DIR, OUTPUT_DIR
from agents import (
    create_ad_researcher,
    create_marketing_analyst,
    create_script_writer,
    create_video_producer,
)
from tasks import (
    create_research_task,
    create_analysis_task,
    create_script_task,
    create_video_task,
)


# ── Logging setup ─────────────────────────────────────────────────────────────

def configure_logging():
    log_file = LOGS_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger.remove()
    logger.add(sys.stderr, level="INFO", colorize=True,
               format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
    logger.add(log_file, level="DEBUG", rotation="10 MB")
    logger.info(f"Logs → {log_file}")


# ── Result helpers ────────────────────────────────────────────────────────────

def _safe_load_json(path: Path) -> dict | list | None:
    """Load a JSON file produced by the crew, handling minor formatting issues."""
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception as exc:
        logger.warning(f"Could not parse JSON from {path}: {exc}")
        return None


def print_summary(results: dict):
    """Print a human-readable summary after the run."""
    separator = "─" * 60
    print(f"\n{separator}")
    print("  🎯  CROWDWISDOM ADS AGENT – RUN COMPLETE")
    print(separator)

    # Script preview
    script_path = OUTPUT_DIR / "ad_script.json"
    if script_path.exists():
        data = _safe_load_json(script_path)
        if data and "full_script_text" in data:
            print("\n📝  AD SCRIPT PREVIEW (first 300 chars):")
            print(data["full_script_text"][:300] + " …")

    # Output files
    print(f"\n📁  Output files in: {OUTPUT_DIR}/")
    for fname in ["raw_ads.json", "marketing_analysis.json", "ad_script.json", "video_brief.json"]:
        p = OUTPUT_DIR / fname
        status = "✅" if p.exists() else "❌"
        size = f"({p.stat().st_size // 1024} KB)" if p.exists() else ""
        print(f"   {status}  {fname} {size}")

    print(f"\n{separator}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    configure_logging()
    logger.info("Initialising agents …")

    # Agents
    researcher = create_ad_researcher()
    analyst    = create_marketing_analyst()
    writer     = create_script_writer()
    producer   = create_video_producer()

    # Tasks (sequential – each feeds context into the next)
    t1_research  = create_research_task(researcher)
    t2_analysis  = create_analysis_task(analyst, t1_research)
    t3_script    = create_script_task(writer, t2_analysis)
    t4_video     = create_video_task(producer, t3_script)

    # Crew
    crew = Crew(
        agents=[researcher, analyst, writer, producer],
        tasks=[t1_research, t2_analysis, t3_script, t4_video],
        process=Process.sequential,
        verbose=True,
        memory=False,
    )

    logger.info("🚀 Kicking off the crew …")
    result = crew.kickoff()

    logger.info("✅ Crew finished.")
    print_summary(result)
    return result


if __name__ == "__main__":
    run()
