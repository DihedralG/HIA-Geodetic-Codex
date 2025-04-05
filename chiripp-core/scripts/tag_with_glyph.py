import hashlib
import json
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Constants
GLYPH_ICON_PATH = "chiripp-core/glyphs/default_glyph.png"  # Replace with your actual glyph
OUTPUT_DIR = "chiripp-core/output/"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_hash(filepath):
    with open(filepath, "rb") as f:
        file_bytes = f.read()
        return hashlib.sha256(file_bytes).hexdigest()

def tag_image_with_glyph(input_path, ai_contribution=0.0, author="Unknown"):
    img = Image.open(input_path).convert("RGBA")
    glyph = Image.open(GLYPH_ICON_PATH).convert("RGBA")

    # Resize glyph
    glyph_size = int(min(img.size) * 0.15)
    glyph = glyph.resize((glyph_size, glyph_size))

    # Paste glyph in bottom-right corner
    position = (img.width - glyph_size - 10, img.height - glyph_size - 10)
    img.paste(glyph, position, glyph)

    # Create metadata
    hash_id = generate_hash(input_path)
    timestamp = datetime.utcnow().isoformat()

    metadata = {
        "hash": hash_id,
        "timestamp_utc": timestamp,
        "author": author,
        "ai_contribution": ai_contribution,
        "original_file": os.path.basename(input_path),
        "glyph_overlay_position": "bottom-right",
        "version": "ChiRIPP v1.0"
    }

    # Save new image
    output_image_path = os.path.join(OUTPUT_DIR, f"tagged_{os.path.basename(input_path)}")
    img.save(output_image_path)

    # Save metadata
    metadata_path = os.path.splitext(output_image_path)[0] + ".json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"Image tagged and saved to: {output_image_path}")
    print(f"Metadata saved to: {metadata_path}")

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tag_with_glyph.py path/to/image.jpg")
    else:
        tag_image_with_glyph(sys.argv[1], ai_contribution=0.25, author="Glenn C. Andersen")
