# vabot/phase1_connectors.py
import os
import requests


# -------------------------------
# Instagram Reels
# -------------------------------
def instagram_reels():
    username = os.getenv("IG_USER")
    password = os.getenv("IG_PASS")
    # TODO: Replace with API / Selenium login
    return {
        "platform": "Instagram Reels",
        "followers": 15230,
        "views_yesterday": 23500,
        "revenue_est": "₹25,000"
    }


# -------------------------------
# Printify POD Store
# -------------------------------
def printify_store():
    token = os.getenv("PRINTIFY_API")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    # TODO: requests.get("https://api.printify.com/v1/shops.json", headers=headers)
    return {
        "platform": "Printify POD Store",
        "orders_yesterday": 12,
        "revenue_yesterday": "₹18,500",
        "balance": "₹45,000"
    }


# ---- MESHY AI STORE (LIVE) ----
import os, json, requests
from datetime import datetime, timedelta


def meshy_store():
    api_key = os.getenv("MESHY_API_KEY")
    stats_url = os.getenv(
        "MESHY_STATS_URL")  # e.g., https://api.meshy.yourapp.com/v1/stats

    if not api_key:
        return {
            "platform": "Meshy AI Store",
            "status": "❌ MESHY_API_KEY missing"
        }
    if not stats_url:
        return {
            "platform": "Meshy AI Store",
            "status": "❌ MESHY_STATS_URL missing (set your stats endpoint)"
        }

    # Yesterday window (IST-friendly but service expects UTC unless your API says otherwise)
    today = datetime.utcnow().date()
    yday = today - timedelta(days=1)
    params = {"date_from": yday.isoformat(), "date_to": today.isoformat()}

    try:
        r = requests.get(
            stats_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            },
            params=params,
            timeout=20,
        )
        if r.status_code != 200:
            return {
                "platform": "Meshy AI Store",
                "status": f"❌ API {r.status_code}",
                "detail": r.text[:200]
            }

        data = r.json()

        # Flexible parsing: try common shapes
        # 1) direct totals
        orders = (data.get("orders_yesterday") or data.get("orders")
                  or data.get("count") or 0)
        revenue = (data.get("revenue_yesterday") or data.get("revenue")
                   or data.get("total_amount") or 0)

        # 2) or accumulate from list items
        if isinstance(data, list):
            orders = len(data)
            revenue = sum((item.get("total") or item.get("amount") or 0)
                          for item in data if isinstance(item, dict))

        # 3) or nested payloads
        if isinstance(data, dict) and "items" in data and isinstance(
                data["items"], list):
            orders = len(data["items"])
            revenue = sum((it.get("total") or it.get("amount") or 0)
                          for it in data["items"] if isinstance(it, dict))

        return {
            "platform": "Meshy AI Store",
            "orders_yesterday": orders,
            "revenue_yesterday": revenue,
            "note": "✅ Live Meshy stats"
        }

    except requests.RequestException as e:
        return {
            "platform": "Meshy AI Store",
            "status": "❌ Network error",
            "detail": str(e)
        }
    except (ValueError, json.JSONDecodeError) as e:
        return {
            "platform": "Meshy AI Store",
            "status": "❌ Bad JSON",
            "detail": str(e)[:200]
        }


# -------------------------------
# Cad Crowd Auto Work
# -------------------------------
def cadcrowd_auto():
    # TODO: API / scraping
    return {
        "platform": "Cad Crowd Auto Work",
        "projects_done": 2,
        "earnings_yesterday": "₹30,000"
    }


# -------------------------------
# Fiverr AI Gig Automation
# -------------------------------
def fiverr_ai():
    # TODO: Fiverr API / scraping
    return {
        "platform": "Fiverr AI Gig Automation",
        "orders": 3,
        "earnings_yesterday": "₹18,000"
    }


# -------------------------------
# Upwork Freelance Work
# -------------------------------
def upwork():
    return {
        "platform": "Upwork",
        "contracts": 1,
        "earnings_yesterday": "₹12,500"
    }


# -------------------------------
# Redbubble POD
# -------------------------------
def redbubble():
    return {
        "platform": "Redbubble POD",
        "orders_yesterday": 5,
        "revenue_yesterday": "₹7,200"
    }


# -------------------------------
# Etsy Store
# -------------------------------
def etsy_store():
    return {
        "platform": "Etsy Store",
        "orders": 6,
        "revenue_yesterday": "₹9,800"
    }


# -------------------------------
# Freelancer.com Work
# -------------------------------
def freelancer_work():
    return {
        "platform": "Freelancer.com",
        "projects_done": 1,
        "earnings_yesterday": "₹6,500"
    }


# -------------------------------
# Amazon KDP (Publishing)
# -------------------------------
def amazon_kdp():
    return {
        "platform": "Amazon KDP",
        "books_sold": 15,
        "royalties_yesterday": "₹12,000"
    }


# -------------------------------
# EXPORT ALL
# -------------------------------
CONNECTORS = [
    instagram_reels, printify_store, meshy_store, cadcrowd_auto, fiverr_ai,
    upwork, redbubble, etsy_store, freelancer_work, amazon_kdp
]
