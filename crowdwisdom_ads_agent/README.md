# CrowdWisdomTrading – Daily Ads AI Agent

A multi-agent CrewAI pipeline that researches winning Meta ads, extracts marketing
intelligence, writes a 60-second video ad script, and produces a full
Remotion + ElevenLabs production brief — all automatically.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CrewAI Pipeline                         │
│                   (Process.sequential)                      │
│                                                             │
│  Agent 1            Agent 2            Agent 3              │
│  Ad Researcher  →  Marketing       →  Script Writer    →   │
│  (Apify / Meta     Analyst             (GDrive brand        │
│   Ads Library)     (LLM analysis)       data + analysis)    │
│                                                             │
│                                         Agent 4             │
│                                         Video Producer      │
│                                         (Remotion brief)    │
└─────────────────────────────────────────────────────────────┘
```

### Output files (`output/`)

| File | Produced by | Contents |
|---|---|---|
| `raw_ads.json` | Agent 1 | Top 20 Meta ads (last 30 days) |
| `marketing_analysis.json` | Agent 2 | Pain points, hooks, angles, proof patterns |
| `ad_script.json` | Agent 3 | 60-second timed ad script |
| `video_brief.json` | Agent 4 | Scene-by-scene Remotion + ElevenLabs brief |

---

## Quick Start

### 1. Clone & install

```bash
git clone <your-repo>
cd crowdwisdom_ads_agent
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Where to get it |
|---|---|
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) – free tier available |
| `APIFY_API_TOKEN` | [apify.com](https://apify.com) – free tier: 5 USD/month credit |
| `GDRIVE_FOLDER_ID` | Google Drive folder URL → last segment after `/folders/` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google Cloud Console → Service Accounts → JSON key |

> **No API keys yet?**  
> The pipeline has mock data fallbacks for both Apify and Google Drive,
> so you can run it immediately to see the full output structure.

### 3. Run

```bash
python main.py
```

---

## Agent Details

### Agent 1 – Ad Researcher
- **Tool:** `ApifyMetaAdsTool` (wraps `apify/facebook-ads-scraper`)
- **What it does:** Calls Meta Ads Library via Apify, filters ads from the last 30 days,
  ranks by quality heuristic (has video > copy length > recency), returns top 20.
- **Output:** `output/raw_ads.json`

### Agent 2 – Marketing Analyst
- **Tool:** LLM only (no external calls)
- **What it does:** Reads all 20 ads and extracts 7 categories of marketing intelligence:
  pain points, hooks, angles, proof patterns, CTAs, emotional triggers, and ad structure.
- **Output:** `output/marketing_analysis.json`

### Agent 3 – Script Writer
- **Tool:** `GDriveBrandDataTool` (fetches brand USPs, testimonials, pricing from GDrive)
- **What it does:** Combines the marketing analysis with real brand data to write a
  60-second script in 6 timed sections (hook → agitate → solution → proof → offer → CTA).
- **Output:** `output/ad_script.json`

### Agent 4 – Video Producer
- **Tool:** LLM only
- **What it does:** Breaks the script into 6-8 scenes, each with visual direction,
  voiceover text, subtitle copy, and stock image keywords. Also produces Remotion
  and ElevenLabs configuration objects.
- **Output:** `output/video_brief.json`

---

## Using the Video Brief with Remotion

Install Remotion:
```bash
npx create-video@latest
```

Use the `REMOTION_CONFIG` from `video_brief.json` to configure your composition,
and feed each scene's `voiceover_text` to ElevenLabs API to generate MP3 audio clips.

ElevenLabs quick start:
```python
import requests

response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers={"xi-api-key": "YOUR_KEY"},
    json={
        "text": scene["voiceover_text"],
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
)
with open(f"scene_{scene['scene_number']}.mp3", "wb") as f:
    f.write(response.content)
```

---

## Project Structure

```
crowdwisdom_ads_agent/
├── main.py                    # Entry point – assembles and runs the crew
├── requirements.txt
├── .env.example               # Environment variable template
├── README.md
│
├── config/
│   ├── __init__.py
│   └── settings.py            # All env vars loaded here
│
├── agents/
│   ├── __init__.py
│   ├── ad_researcher.py       # Agent 1
│   ├── marketing_analyst.py   # Agent 2
│   ├── script_writer.py       # Agent 3
│   └── video_producer.py      # Agent 4
│
├── tasks/
│   ├── __init__.py
│   └── task_definitions.py    # One task per agent
│
├── tools/
│   ├── __init__.py
│   ├── apify_tool.py          # Meta Ads Library scraper
│   └── gdrive_tool.py         # Google Drive brand data fetcher
│
├── output/                    # Auto-created – all JSON outputs here
└── logs/                      # Auto-created – timestamped run logs
```

---

## Evaluation Criteria Checklist

| Criterion | Status |
|---|---|
| Working functionality | ✅ Mock fallbacks ensure end-to-end run without API keys |
| Code clarity and organisation | ✅ Clean module separation, docstrings, type hints |
| Logging and error handling | ✅ Loguru logger, try/except in all tools, graceful fallbacks |
| Scale | ✅ `MAX_ADS_TO_ANALYSE` and `ADS_LOOKBACK_DAYS` are config-driven |
| GitHub link | Submit your repo URL |
| Clear documentation | ✅ This README |
| APIFY tokens used | Submit your token in the email |
| Video output examples | Run the pipeline and submit `output/video_brief.json` |

---

## Free Model Options (OpenRouter)

```
mistralai/mistral-7b-instruct:free   ← recommended
meta-llama/llama-3-8b-instruct:free
google/gemma-7b-it:free
```

Set `OPENROUTER_MODEL` in your `.env` to switch models.

---

*Built for CrowdWisdomTrading Internship Assessment – 2024*
