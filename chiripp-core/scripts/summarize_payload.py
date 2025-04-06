
import openai
import os
import json
import sys
from datetime import datetime



# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load JSON payload file
def load_payload(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Generate GPT summary
def generate_summary(json_data):
    prompt = """You are a metadata analyst. Summarize the following metadata payload in markdown format. Include key observations, dataset attributes, and any irregularities or notable patterns.\n\nMetadata:\n""" + json.dumps(json_data, indent=2)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a metadata analyst. Summarize this in markdown."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=600
    )

    return response.choices[0].message.content

# Save to .md
def save_markdown(content, out_dir="/Users/glennandersen/Documents/GitHub/HIA-Geodetic-Codex/chiripp-core/logs/"):
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{out_dir}{timestamp}_summary.md"
    with open(filename, 'w') as f:
        f.write(content)
    print(f"✅ Saved GPT summary to {filename}")

# Run script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 summarize_payload.py <path_to_json>")
        sys.exit(1)

    payload_path = sys.argv[1]
    data = load_payload(payload_path)
    summary = generate_summary(data)
    save_markdown(summary)

