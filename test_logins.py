# test_logins.py
from login_manager import get_login


def mask(p):
    return "(missing)" if not p else "*" * max(4, len(p))


def check(member):
    try:
        email, pw = get_login(member)
        print(
            f"{member.capitalize():5} → {email or '(missing)'} | {mask(pw)} | ✅ OK"
        )
    except Exception as e:
        print(f"{member.capitalize():5} → ❌ {e}")


for m in ["elina", "kael", "riva"]:
    check(m)

print("\nSecrets check completed.")
