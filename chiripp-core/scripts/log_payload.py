import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 log_payload.py <path_to_json>")
        return

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return

    with open(input_path, 'r') as f:
        data = json.load(f)

    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = logs_dir / f"{timestamp}_payload.json"

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Payload saved to: {output_file}")

if __name__ == "__main__":
    main()

