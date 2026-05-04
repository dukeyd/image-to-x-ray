# AGENTS.md

## Project

- Python GUI application for converting images to X-ray style
- Uses tkinter for UI, Pillow for image processing

## Setup & Commands

- `uv sync` - Install dependencies
- `uv run python main.py` - Run the app

## Architecture

- Single file: `main.py` contains all UI and image processing logic
- X-ray effect: grayscale → invert → contrast enhancement → brightness adjustment → blue tint

## Testing

- `uv run python -c "import main"` - Verify imports