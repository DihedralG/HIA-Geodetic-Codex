#!/bin/bash
echo "Running ChiRIPP payload summarizer..."
python3 chiripp-core/scripts/summarize_payload.py chiripp-core/data/sample_tagged_metadata.json

# Optional: copy to a timestamped version
LATEST_FILE=$(ls -t chiripp-core/logs/*_summary.md | head -n1)
cp "$LATEST_FILE" chiripp-core/logs/2025-04-06_15-19-59_summary.md

echo "✅ Summary saved and copied as 2025-04-06_15-19-59_summary.md"