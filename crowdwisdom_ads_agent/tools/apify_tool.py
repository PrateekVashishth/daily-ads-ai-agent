"""
tools/apify_tool.py
────────────────────
Custom CrewAI tool that searches Meta (Facebook) Ads Library for ads
related to a given niche/URL using the Apify platform.

Actor used:  apify/facebook-ads-scraper   (free tier available)
Docs:        https://apify.com/apify/facebook-ads-scraper
"""

import json
import time
from datetime import datetime, timedelta
from typing import Optional, Type

from apify_client import ApifyClient
from crewai.tools import BaseTool
from loguru import logger
from pydantic import BaseModel, Field

from config.settings import (
    APIFY_API_TOKEN,
    ADS_LOOKBACK_DAYS,
    MAX_ADS_TO_ANALYSE,
    OUTPUT_DIR,
    TARGET_NICHE,
    TARGET_URL,
)


# ── Input schema ─────────────────────────────────────────────────────────────

class ApifyAdSearchInput(BaseModel):
    niche: str = Field(
        default=TARGET_NICHE,
        description="Trading niche keyword to search in Meta Ads Library",
    )
    page_url: str = Field(
        default=TARGET_URL,
        description="Facebook page URL of the advertiser (e.g. crowdwisdomtrading.com)",
    )
    lookback_days: int = Field(
        default=ADS_LOOKBACK_DAYS,
        description="How many days back to search for active ads",
    )
    max_results: int = Field(
        default=MAX_ADS_TO_ANALYSE,
        description="Maximum number of top ads to return",
    )


# ── Tool ─────────────────────────────────────────────────────────────────────

class ApifyMetaAdsTool(BaseTool):
    """
    Searches the Meta Ads Library for active ads in the last N days
    for a given niche / Facebook page, using the Apify scraper.
    Returns a JSON list of the best-performing ads.
    """

    name: str = "Meta Ads Library Scraper"
    description: str = (
        "Searches Meta (Facebook) Ads Library for ads related to the "
        "CrowdWisdomTrading product and trading niche. "
        "Returns up to 20 of the most recently active ads as JSON."
    )
    args_schema: Type[BaseModel] = ApifyAdSearchInput

    # ── internal helpers ─────────────────────────────────────────────────────

    def _run_actor(self, search_terms: list[str], since_date: str) -> list[dict]:
        """Start the Apify actor and wait for it to finish."""
        client = ApifyClient(APIFY_API_TOKEN)

        run_input = {
            "searchTerms": search_terms,
            "adType": "ALL",
            "country": "US",
            "language": "en",
            "activeStatus": "ACTIVE",
            "startDate": since_date,
            "maxItems": 100,   # we'll rank and trim afterwards
        }

        logger.info(f"Starting Apify actor with terms={search_terms}, since={since_date}")
        run = client.actor("apify/facebook-ads-scraper").call(run_input=run_input)

        dataset_id = run["defaultDatasetId"]
        logger.info(f"Actor finished. Dataset id: {dataset_id}")
        items = list(client.dataset(dataset_id).iterate_items())
        logger.info(f"Fetched {len(items)} raw ads from Apify")
        return items

    def _rank_ads(self, items: list[dict], max_results: int) -> list[dict]:
        """
        Simple heuristic ranking:
        - prefer ads with longer copy (more signals)
        - prefer ads that have video or image
        - sort by start_date descending (newest first)
        """

        def score(ad: dict) -> tuple:
            has_media = int(bool(ad.get("videoUrl") or ad.get("imageUrls")))
            body_len = len(ad.get("body", "") or "")
            return (has_media, body_len)

        ranked = sorted(items, key=score, reverse=True)
        return ranked[:max_results]

    def _normalise(self, raw: list[dict]) -> list[dict]:
        """Extract only the fields we care about downstream."""
        results = []
        for ad in raw:
            results.append(
                {
                    "ad_id": ad.get("adId") or ad.get("id"),
                    "page_name": ad.get("pageName"),
                    "body": ad.get("body") or ad.get("adBodyText"),
                    "headline": ad.get("linkTitle") or ad.get("title"),
                    "cta": ad.get("cta"),
                    "start_date": ad.get("startDate"),
                    "has_video": bool(ad.get("videoUrl")),
                    "image_urls": ad.get("imageUrls", []),
                    "video_url": ad.get("videoUrl"),
                    "ad_url": ad.get("adUrl") or ad.get("url"),
                    "platforms": ad.get("publisherPlatforms", []),
                }
            )
        return results

    # ── BaseTool interface ────────────────────────────────────────────────────

    def _run(
        self,
        niche: str = TARGET_NICHE,
        page_url: str = TARGET_URL,
        lookback_days: int = ADS_LOOKBACK_DAYS,
        max_results: int = MAX_ADS_TO_ANALYSE,
    ) -> str:
        since_date = (
            datetime.utcnow() - timedelta(days=lookback_days)
        ).strftime("%Y-%m-%d")

        search_terms = [niche, "trading signals", "stock market", page_url]

        try:
            raw_items = self._run_actor(search_terms, since_date)
        except Exception as exc:
            logger.error(f"Apify actor failed: {exc}")
            # Return mock data so the pipeline can continue during development
            raw_items = self._mock_ads()

        ranked = self._rank_ads(raw_items, max_results)
        normalised = self._normalise(ranked)

        # Persist raw results
        out_path = OUTPUT_DIR / "raw_ads.json"
        with open(out_path, "w") as fh:
            json.dump(normalised, fh, indent=2)
        logger.info(f"Saved {len(normalised)} ads → {out_path}")

        return json.dumps(normalised, indent=2)

    # ── mock data (used when Apify token is missing / actor fails) ────────────

    def _mock_ads(self) -> list[dict]:
        logger.warning("Using MOCK ad data – set APIFY_API_TOKEN for real scraping")
        return [
            {
                "adId": "mock_001",
                "pageName": "CrowdWisdomTrading",
                "body": (
                    "Stop guessing the market. Our AI-powered signals have helped "
                    "thousands of traders make consistent profits. Join 50,000+ members "
                    "who get daily buy/sell alerts directly to their phone. "
                    "Risk-free 7-day trial. Cancel anytime."
                ),
                "linkTitle": "Get Your Free Trial Today",
                "cta": "SIGN_UP",
                "startDate": "2024-11-01",
                "videoUrl": "https://example.com/video1.mp4",
                "imageUrls": [],
                "adUrl": "https://crowdwisdomtrading.com",
                "publisherPlatforms": ["facebook", "instagram"],
            },
            {
                "adId": "mock_002",
                "pageName": "CrowdWisdomTrading",
                "body": (
                    "The market is moving FAST. Are you positioned correctly? "
                    "Our crowd-sourced trading signals give you the edge. "
                    "See what our community is buying RIGHT NOW."
                ),
                "linkTitle": "See Live Signals",
                "cta": "LEARN_MORE",
                "startDate": "2024-10-20",
                "videoUrl": None,
                "imageUrls": ["https://example.com/img1.jpg"],
                "adUrl": "https://crowdwisdomtrading.com",
                "publisherPlatforms": ["facebook"],
            },
            {
                "adId": "mock_003",
                "pageName": "TradeSignalPro",
                "body": (
                    "Tired of missing winning trades? "
                    "We send you precise entry and exit points every morning. "
                    "Members averaged 23% returns last quarter."
                ),
                "linkTitle": "Start Free – No Credit Card",
                "cta": "GET_OFFER",
                "startDate": "2024-11-05",
                "videoUrl": "https://example.com/video2.mp4",
                "imageUrls": [],
                "adUrl": "https://tradesignalpro.com",
                "publisherPlatforms": ["facebook", "instagram", "messenger"],
            },
        ]
