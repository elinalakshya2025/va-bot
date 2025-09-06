"""
Clean connectors file for VA Bot Phase 1.
"""

import os, requests
from typing import List, Dict, Any

# -------------------- Printify --------------------
def get_printify_shops() -> List[Dict[str, Any]]:
    api_key = os.getenv("PRINTIFY_API_KEY")
    if not api_key:
        return []
    try:
        resp = requests.get(
            "https://api.printify.com/v1/shops.json",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                return data.get("shops", [])
            return data
        return [{"error": f"{resp.status_code} {resp.text}"}]
    except Exception as e:
        return [{"error": str(e)}]

# -------------------- Meshy --------------------
def get_meshy_shops() -> List[Dict[str, Any]]:
    api_key = os.getenv("MESHY_API_KEY")
    if not api_key:
        return []
    try:
        resp = requests.get(
            "https://api.meshy.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("models", data) if isinstance(data, dict) else data
        return [{"error": f"{resp.status_code} {resp.text}"}]
    except Exception as e:
        return [{"error": str(e)}]

# -------------------- YouTube --------------------
def get_channel_stats(channel_id: str = "UCe2cqtUKLMCm9v9vmsAkKaA") -> dict:
    """
    Fetch stats for Elina Lakshya channel.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return {"error": "YOUTUBE_API_KEY not set", "channel_id": channel_id}
    try:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if items:
                stats = items[0].get("statistics", {})
                return {
                    "subscribers": stats.get("subscriberCount"),
                    "views": stats.get("viewCount"),
                    "videos": stats.get("videoCount"),
                    "channel_id": channel_id,
                }
            return {"error": "No items in response", "channel_id": channel_id}
        return {"error": resp.text, "channel_id": channel_id}
    except Exception as e:
        print("🔎 DEBUG: YouTube API error", e); return {"error": str(e), "channel_id": channel_id}

# -------------------- Other Stubs --------------------
def list_models(): return []
def get_shopify_products(): return []
def get_cadcrowd_jobs(): return []
def get_fiverr_gigs(): return []
def get_stock_image_sync_status(): return {"status": "ok", "detail": "stub"}
def get_kdp_books(): return []
def get_shopify_digital(): return []
def get_stationery_exports(): return []
def generate_api_keys_report(): return {"generated": [], "warnings": []}
def connectors_status(): return {"status": "ok"}
