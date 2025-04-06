# Thread 003a: ChiRIPP Auto-Summarizer + Webhook System (Carryover)

# --- Imports and Setup ---
import os
import json
import requests
from datetime import datetime
import argparse

# Constants
LOGS_DIR = "logs"
WEBHOOK_URL = "https://hook.us2.make.com/rcb15x7djnvswaugus1pqrpixa3cbdby"  # ChiRIPP webhook

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# --- Summarizer Function (Placeholder for GPT/OpenAI Call) ---
def generate_summary(input_text):
    """Stub for GPT-based summarization."""
    return f"SUMMARY: {input_text[:75]}..."

# --- Metadata Generator ---
def generate_metadata(file_path, author="Unknown"):
    base = os.path.basename(file_path)
    return {
        "id": base.replace(".txt", "").replace(".md", ""),
        "source": "cli_upload",
        "author": author,
        "retention_policy": "24h",
        "doc_type": "text"
    }

# --- Handler Function ---
def handle_new_submission(input_text, metadata):
    timestamp = datetime.utcnow().isoformat()
    summary = generate_summary(input_text)

    # Compose payload
    payload = {
        "timestamp": timestamp,
        "metadata": metadata,
        "summary": summary,
        "full_text": input_text
    }

    # Save log
    log_filename = os.path.join(LOGS_DIR, f"log_{metadata['id']}.json")
    with open(log_filename, "w") as f:
        json.dump(payload, f, indent=2)

    # Post to Make.com webhook
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"✅ Successfully posted to webhook: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Webhook post failed: {e}")

# --- CLI Entry Point ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChiRIPP CLI Uploader")
    parser.add_argument("filepath", help="Path to .txt or .md file")
    parser.add_argument("--author", help="Name of author", default="Glenn C. Andersen")
    args = parser.parse_args()

    if not os.path.exists(args.filepath):
        print("❌ File not found.")
        exit(1)

    with open(args.filepath, "r", encoding="utf-8") as f:
        input_text = f.read()

    metadata = generate_metadata(args.filepath, args.author)
    handle_new_submission(input_text, metadata)
