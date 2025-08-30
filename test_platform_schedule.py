# test_platform_schedule.py
from login_manager import list_active_platforms, next_activation_after, get_platform_login
from zoneinfo import ZoneInfo
from datetime import datetime

IST = ZoneInfo("Asia/Kolkata")
now = datetime.now(IST)

print("Now IST:", now.strftime("%Y-%m-%d %H:%M"))
print("\nACTIVE PLATFORMS:")
for pid, title, member, act in list_active_platforms(now):
    print(f" - {title} ({pid}) | Owner: {member} | since {act}")

nxt = next_activation_after(now)
if nxt:
    pid, title, member, act = nxt
    print(f"\nNEXT ACTIVATION: {title} ({pid}) by {member} on {act}")

# Example: fetch creds for a platform (will raise if not yet active or secret missing)
try:
    email, pw = get_platform_login("printify_pod")
    print(f"\nCreds OK for printify_pod → {email} | {'*' * len(pw)}")
except Exception as e:
    print(f"\nprintify_pod → {e}")
