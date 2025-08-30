# test_platforms.py
from login_manager import (
    list_active_platforms,
    next_activation_after,
    get_platform_login,
    PLATFORM_SCHEDULE,
)
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def mask(p): 
    return "(missing)" if not p else "*" * max(4, len(p))

now = datetime.now(IST)
print("Now IST:", now.strftime("%Y-%m-%d %H:%M"))

print("\n=== ACTIVE PLATFORMS ===")
active = list_active_platforms(now)
if not active:
    print("None active yet.")
else:
    for pid, title, member, start in active:
        print(f"✅ {title} ({pid}) — owner: {member}, since {start}")

nxt = next_activation_after(now)
print("\n=== NEXT ACTIVATION ===")
if nxt:
    pid, title, member, start = nxt
    print(f"⏳ {title} ({pid}) — owner: {member}, activates on {start}")
else:
    print("🎉 All platforms already active.")

print("\n=== CREDENTIAL CHECK (all 30) ===")
for pid, meta in PLATFORM_SCHEDULE.items():
    title, owner = meta["title"], meta["member"]
    try:
        email, pw = get_platform_login(pid)
        print(f"OK  → {title:30} ({pid:22}) | owner: {owner:5} | {email} | {mask(pw)}")
    except Exception as e:
        print(f"ERR → {title:30} ({pid:22}) | owner: {owner:5} | {e}")

print("\nCheck complete.")
