"""
tools/gdrive_tool.py
──────────────────────
Custom CrewAI tool that fetches brand/product data files from a
Google Drive folder using a service-account credential.

The agent uses this data (testimonials, USPs, product features, pricing)
to ground the ad script in real, accurate information.
"""

import io
import json
from typing import Optional, Type

from crewai.tools import BaseTool
from loguru import logger
from pydantic import BaseModel, Field

from config.settings import GDRIVE_FOLDER_ID, GOOGLE_SERVICE_ACCOUNT_JSON, OUTPUT_DIR

# Google API imports are optional – gracefully degrade if not installed
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload

    _GDRIVE_AVAILABLE = True
except ImportError:
    _GDRIVE_AVAILABLE = False
    logger.warning("google-api-python-client not installed. GDrive tool will use mock data.")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


# ── Input schema ─────────────────────────────────────────────────────────────

class GDriveInput(BaseModel):
    folder_id: str = Field(
        default=GDRIVE_FOLDER_ID,
        description="Google Drive folder ID that contains brand data files",
    )


# ── Tool ─────────────────────────────────────────────────────────────────────

class GDriveBrandDataTool(BaseTool):
    """
    Fetches brand / product data from a Google Drive folder.
    Returns a structured JSON string with: USPs, pain points,
    testimonials, pricing, and product features.
    """

    name: str = "Google Drive Brand Data Fetcher"
    description: str = (
        "Downloads brand and product data files from a designated Google Drive folder. "
        "Returns key marketing information: USPs, pain points, testimonials, "
        "pricing, and product features to be used in ad copy."
    )
    args_schema: Type[BaseModel] = GDriveInput

    # ── internal helpers ─────────────────────────────────────────────────────

    def _build_service(self):
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES
        )
        return build("drive", "v3", credentials=creds)

    def _list_files(self, service, folder_id: str) -> list[dict]:
        query = f"'{folder_id}' in parents and trashed=false"
        result = (
            service.files()
            .list(q=query, fields="files(id, name, mimeType)")
            .execute()
        )
        return result.get("files", [])

    def _download_text(self, service, file_id: str) -> str:
        request = service.files().get_media(fileId=file_id)
        buf = io.BytesIO()
        dl = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = dl.next_chunk()
        return buf.getvalue().decode("utf-8", errors="ignore")

    def _parse_files(self, service, files: list[dict]) -> dict:
        brand_data: dict = {}
        for f in files:
            name = f["name"].lower()
            try:
                content = self._download_text(service, f["id"])
                if name.endswith(".json"):
                    brand_data[f["name"]] = json.loads(content)
                else:
                    brand_data[f["name"]] = content
                logger.info(f"Downloaded GDrive file: {f['name']}")
            except Exception as exc:
                logger.error(f"Failed to download {f['name']}: {exc}")
        return brand_data

    # ── BaseTool interface ────────────────────────────────────────────────────

    def _run(self, folder_id: str = GDRIVE_FOLDER_ID) -> str:
        if not _GDRIVE_AVAILABLE or not folder_id:
            logger.warning("GDrive unavailable or folder_id not set – using mock brand data")
            data = self._mock_brand_data()
        else:
            try:
                service = self._build_service()
                files = self._list_files(service, folder_id)
                if not files:
                    logger.warning("No files found in GDrive folder – using mock data")
                    data = self._mock_brand_data()
                else:
                    data = self._parse_files(service, files)
            except Exception as exc:
                logger.error(f"GDrive fetch failed: {exc} – falling back to mock data")
                data = self._mock_brand_data()

        out_path = OUTPUT_DIR / "brand_data.json"
        with open(out_path, "w") as fh:
            json.dump(data, fh, indent=2)
        logger.info(f"Brand data saved → {out_path}")

        return json.dumps(data, indent=2)

    # ── mock data ─────────────────────────────────────────────────────────────

    def _mock_brand_data(self) -> dict:
        return {
            "product_name": "CrowdWisdomTrading Signals",
            "tagline": "Trade smarter with the crowd",
            "unique_selling_points": [
                "AI + crowd-sourced signal fusion",
                "Real-time buy/sell alerts via SMS and app",
                "Transparent track record – every signal logged",
                "Risk management built-in (stop-loss levels included)",
                "7-day free trial, cancel any time",
            ],
            "pain_points": [
                "Missing winning trades due to information overload",
                "Emotional trading decisions leading to losses",
                "Expensive or unreliable trading services",
                "No time to research the market every day",
                "Feeling left behind while others profit",
            ],
            "testimonials": [
                {
                    "name": "Marcus T.",
                    "result": "Up 31% in 3 months following the daily signals",
                },
                {
                    "name": "Priya S.",
                    "result": "Finally stopped impulse trading. Clear entry/exit points changed everything.",
                },
                {
                    "name": "David R.",
                    "result": "Recouped my annual subscription in the first week.",
                },
            ],
            "pricing": {
                "monthly": "$49/mo",
                "annual": "$399/yr (save 32%)",
                "trial": "7 days free",
            },
            "features": [
                "Daily pre-market briefing",
                "3-5 high-conviction trade ideas per day",
                "Portfolio tracker",
                "Community chat with 50,000+ members",
                "Educational video library",
            ],
            "target_audience": "retail traders aged 25-55 who trade stocks, options, or crypto",
        }
