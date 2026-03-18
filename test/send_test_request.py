import json
import requests
from pathlib import Path

# --- Configuration ---
SERVER_URL = "http://localhost:5002/convert"
SOURCE_LANGUAGE = "LinkMl"
TARGET_LANGUAGE = "JsonSchema"
SCHEMA_FILE = Path("schemas/linkml.yaml")


def main():
    # Load schema from file as string
    with open(SCHEMA_FILE, "r") as f:
        schema_str = f.read()

    # Build payload
    payload = {
        "sourceLanguage": SOURCE_LANGUAGE,
        "targetLanguage": TARGET_LANGUAGE,
        "schema": schema_str
    }

    # Send request
    print(f"Sending conversion request {SOURCE_LANGUAGE} → {TARGET_LANGUAGE} ...")
    resp = requests.post(SERVER_URL, json=payload)

    # Handle response
    if resp.status_code == 200:
        result = resp.json()
        print("Conversion Results:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error {resp.status_code}: {resp.text}")


if __name__ == "__main__":
    main()
