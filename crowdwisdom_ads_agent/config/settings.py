"""
config/settings.py
──────────────────
Central settings loaded from environment variables via python-dotenv.
All other modules import from here – never read os.environ directly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one level above config/)
load_dotenv(Path(__file__).parent.parent / ".env")


# ── LLM ───────────────────────────────────────────────────────
OPENROUTER_API_KEY: str = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_MODEL: str = os.getenv(
    "OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free"
)
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

# ── Apify ─────────────────────────────────────────────────────
APIFY_API_TOKEN: str = os.environ["APIFY_API_TOKEN"]

# ── Google Drive ──────────────────────────────────────────────
GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_JSON", "credentials/service_account.json"
)
GDRIVE_FOLDER_ID: str = os.getenv("GDRIVE_FOLDER_ID", "")

# ── Target ────────────────────────────────────────────────────
TARGET_NICHE: str = os.getenv("TARGET_NICHE", "trading")
TARGET_URL: str = os.getenv("TARGET_URL", "https://crowdwisdomtrading.com")

# ── Paths ─────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / os.getenv("OUTPUT_DIR", "output")
LOGS_DIR = PROJECT_ROOT / os.getenv("LOGS_DIR", "logs")

OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ── Scraping ──────────────────────────────────────────────────
ADS_LOOKBACK_DAYS: int = 30          # last N days of Meta ads
MAX_ADS_TO_ANALYSE: int = 20         # top N ads forwarded to Agent 2
