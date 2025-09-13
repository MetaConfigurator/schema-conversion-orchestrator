import json
import requests
from pathlib import Path

# --- Configuration ---
SERVER_URL = "http://localhost:5002/convert"
SOURCE_FORMAT = "JsonSchema"
TARGET_FORMAT = "GraphQl"
SCHEMA_FILE = Path("schemas/simpleSchema.schema.json")


def main():
    # Load schema from file
    with SCHEMA_FILE.open("r", encoding="utf-8") as f:
        schema_dict = json.load(f)

    # Convert schema dict to a JSON string (your Flask server expects str)
    schema_str = json.dumps(schema_dict)

    # Build payload
    payload = {
        "sourceFormat": SOURCE_FORMAT,
        "targetFormat": TARGET_FORMAT,
        "schema": schema_str
    }

    # Send request
    print(f"Sending conversion request {SOURCE_FORMAT} → {TARGET_FORMAT} ...")
    resp = requests.post(SERVER_URL, json=payload)

    # Handle response
    if resp.status_code == 200:
        result = resp.json()
        print("Conversion successful!\n")
        print(result["schema"])
    else:
        print(f"Error {resp.status_code}: {resp.text}")


if __name__ == "__main__":
    main()
