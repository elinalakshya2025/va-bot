"""
test_va_bot.py - VA Bot test script
✅ Works with secret-folder amounts
✅ Tests /health, /test_email, /approve endpoints
✅ Can run while main.py is running in background
"""

import requests
import time

BASE_URL = 'http://127.0.0.1:3000'  # Make sure main.py uses PORT=3000
APPROVAL_TEST_TOKEN = 'testtoken123456'


def test_health():
    try:
        r = requests.get(f'{BASE_URL}/health')
        print(f"[Health] {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[Health] Error: {e}")


def test_email():
    try:
        r = requests.get(f'{BASE_URL}/test_email')
        print(f"[Test Email] {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[Test Email] Error: {e}")


def test_approval():
    try:
        r = requests.get(f'{BASE_URL}/approve?token={APPROVAL_TEST_TOKEN}')
        print(f"[Approval] {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[Approval] Error: {e}")


if __name__ == "__main__":
    print("=== Starting VA Bot Test ===")
    time.sleep(5)  # Wait a few seconds if server just started
    test_health()
    test_email()
    test_approval()
    print(
        "=== VA Bot test script finished. Server still running in background ==="
    )
