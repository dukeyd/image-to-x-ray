# AGENTS.md

## Project

- Python CLI tool for converting images to X-ray style
- Uses Pillow for image processing

## Setup & Commands

- `uv sync` - Install dependencies
- `uv run python main.py <input_folder> <output_folder>` - Run CLI (e.g., `uv run python main.py input output`)

## Deployment

For Railway or similar containers (no GUI):
- Run as CLI: `python main.py /input /output`
- Mount volumes for input/output folders