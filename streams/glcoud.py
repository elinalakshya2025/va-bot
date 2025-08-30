import os
import json
from google.oauth2 import service_account
import google.auth

# Load JSON from environment variable
service_account_info = json.loads(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info)


def setup_gcloud():
    # Load JSON from env
    creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not creds_json:
        raise ValueError(
            "❌ Missing GOOGLE_APPLICATION_CREDENTIALS_JSON env var")

    creds_dict = json.loads(creds_json)

    # Build credentials object
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict)

    # Set GOOGLE_APPLICATION_CREDENTIALS to a temp file (for SDKs needing file)
    temp_path = "/tmp/gcloud-key.json"
    with open(temp_path, "w") as f:
        f.write(creds_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path

    print("✅ Google Cloud credentials loaded into environment")


if __name__ == "__main__":
    setup_gcloud()
    print("VA Bot ready with Google Cloud creds (via Render env vars)")
