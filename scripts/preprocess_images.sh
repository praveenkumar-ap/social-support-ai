#!/usr/bin/env bash
#
# preprocess_images.sh
# Preprocess images: convert to PNG, resize, and perform OCR-friendly adjustments.
#
# Usage:
#   ./preprocess_images.sh --input-dir data/raw/images --output-dir data/processed/images
#

set -euo pipefail

# Default directories (can be overridden by env vars)
INPUT_DIR=${INPUT_IMAGES_DIR:-"data/raw/images"}
OUTPUT_DIR=${OUTPUT_IMAGES_DIR:-"data/processed/images"}

# Ensure required tools are installed: ImageMagick 'convert'
command -v convert >/dev/null 2>&1 || { echo >&2 "ImageMagick 'convert' is required but not installed."; exit 1; }

usage() {
  echo "Usage: $0 [--input-dir <input_dir>] [--output-dir <output_dir>]"
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input-dir)
      INPUT_DIR="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

# Validate directories
if [[ ! -d "$INPUT_DIR" ]]; then
  echo "Input directory '$INPUT_DIR' does not exist." >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Process images
shopt -s nullglob
for img in "$INPUT_DIR"/*.{jpg,jpeg,png,tiff,bmp}; do
  filename=$(basename "$img")
  base="${filename%.*}"
  output_file="$OUTPUT_DIR/${base}.png"

  echo "Processing '$img' -> '$output_file'"
  # Convert to grayscale, resize to max width 1024, and normalize
  convert "$img" -colorspace Gray -resize 1024x -normalize "$output_file"
done

echo "Image preprocessing completed. Output in '$OUTPUT_DIR'."