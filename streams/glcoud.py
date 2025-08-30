import subprocess, os, glob, sys


def run(cmd):
    print("➤", " ".join(cmd))
    subprocess.run(cmd, check=True)


# --- STEP 1: AUTHENTICATE WITH SERVICE ACCOUNT JSON ---
json_files = glob.glob("*.json")
if not json_files:
    print("❌ No service account JSON found in workspace! Upload it first.")
    sys.exit(1)

key_file = json_files[0]
print(f"🔑 Using service account key: {key_file}")

# Activate service account
run(["gcloud", "auth", "activate-service-account", "--key-file", key_file])

# Show active account
run(["gcloud", "auth", "list"])

# --- STEP 2: GET USER INPUT ---
PROJECT_ID = input("Enter GCP PROJECT_ID: ").strip()
EMAIL = input("Sender Gmail (EMAIL): ").strip()
APP_PASS = input("Gmail App Password (APP_PASS): ").strip()
PAYPAL_EMAIL = input("PayPal Email (PAYPAL_EMAIL): ").strip()

REGION = "asia-south1"
IMAGE = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/va-bot/va-bot:latest"

# --- STEP 3: CONFIGURE PROJECT ---
run(["gcloud", "config", "set", "project", PROJECT_ID])
run(["gcloud", "config", "set", "run/region", REGION])

# --- STEP 4: ENABLE REQUIRED SERVICES ---
run([
    "gcloud", "services", "enable", "run.googleapis.com",
    "cloudbuild.googleapis.com", "artifactregistry.googleapis.com",
    "cloudscheduler.googleapis.com", "secretmanager.googleapis.com"
])


# --- STEP 5: CREATE / UPDATE SECRETS ---
def upsert_secret(name, value):
    try:
        run([
            "bash", "-c",
            f"echo -n '{value}' | gcloud secrets create {name} --data-file=-"
        ])
    except subprocess.CalledProcessError:
        run([
            "bash", "-c",
            f"echo -n '{value}' | gcloud secrets versions add {name} --data-file=-"
        ])


upsert_secret("EMAIL", EMAIL)
upsert_secret("APP_PASS", APP_PASS)
upsert_secret("PAYPAL_EMAIL", PAYPAL_EMAIL)

# --- STEP 6: CREATE ARTIFACT REPO ---
try:
    run([
        "gcloud", "artifacts", "repositories", "create", "va-bot",
        "--repository-format=docker", f"--location={REGION}",
        "--description=Lakshya VA Bot images"
    ])
except subprocess.CalledProcessError:
    print("ℹ️ Repo already exists, skipping.")

# --- STEP 7: BUILD & PUSH IMAGE ---
run(["gcloud", "builds", "submit", "--tag", IMAGE])

print("🎯 Done Boss! VA Bot is built and pushed to Artifact Registry.")
