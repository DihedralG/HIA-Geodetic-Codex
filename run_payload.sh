#!/bin/bash
echo "Running ChiRIPP payload summarizer..."
python3 chiripp-core/scripts/summarize_payload.py chiripp-core/data/sample_tagged_metadata.json

# Optional: copy to a timestamped version
LATEST_FILE=$(ls -t chiripp-core/logs/*_summary.md | head -n1)
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
cp "$LATEST_FILE" chiripp-core/logs/${TIMESTAMP}_summary.md
echo "✅ Summary saved and copied as ${TIMESTAMP}_summary.md"

# Send to Make.com webhook
curl -X POST https://hook.us2.make.com/rcb15x7djnvswaugus1pqrpixa3cbdby \
  -H "Content-Type: application/json" \
  -d "{\"filename\": \"${TIMESTAMP}_summary.md\", \"content\": \"$(cat chiripp-core/logs/${TIMESTAMP}_summary.md | sed 's/"/\\"/g')\"}"