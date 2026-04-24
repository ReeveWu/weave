<div align="center">

<div style="margin: 20px 0;">
  <img src="./assets/logo.png" height="60" alt="Weave Logo" >
</div>

# Weave

**Weave your lecture slides into comprehensive, structured Markdown handouts with AI.**

*Never miss a detail from your lecture slides again.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg)](https://ai.google.dev/)

[English](#features) | [繁體中文](README.zh.md)

</div>

---

Weave is an AI-powered CLI tool designed to transform PDF slides into structured Markdown study guides. Much like its namesake, Weave interlaces scattered slide content into a cohesive and comprehensive learning resource.

## Features

- **Two-Pass AI Analysis** — First generates a structured outline, then expands each chapter with full context
- **PDF to Handout** — Converts multi-page PDF slides into a single, well-organized Markdown document
- **Smart Image Embedding** — Automatically identifies and embeds important charts, diagrams, and formulas
- **Coverage Verification** — Ensures every single slide page is referenced in the final handout
- **Multi-language Output** — Generate handouts in any language (default: Chinese)
- **Zero Content Loss** — Preserves ALL information from slides, including footnotes and small annotations
- **PDF Export** — One command to convert Markdown handouts to beautifully styled PDFs
- **Powered by Gemini** — Leverages Google's multimodal AI with large context window

## Quick Start

### Prerequisites

- Python 3.10+
- [Poppler](https://poppler.freedesktop.org/) (required by `pdf2image` for PDF rendering)
- [Pango](https://www.gtk.org/docs/architecture/pango) (required by `weasyprint` for PDF export)
- A [Google Gemini API key](https://aistudio.google.com/apikey)

```bash
# macOS
brew install poppler pango

# Ubuntu / Debian
sudo apt-get install poppler-utils libpango-1.0-0 libpangoft2-1.0-0

# Windows (chocolatey)
choco install poppler
# See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html for GTK/Pango on Windows
```

### Installation

```bash
# Clone the repository
git clone https://github.com/ReeveWu/weave.git
cd weave

# Install the package (editable mode for development)
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Setup

```bash
# Copy the example env file and add your API key
cp .env.example .env
# Edit .env and replace 'your_api_key_here' with your actual Gemini API key
```

### Usage

```bash
# Place your PDF slides in ./data/, then:
weave

# Or specify custom paths:
weave -i ./my-slides -o ./my-notes

# Use a specific model:
weave -m gemini-2.5-pro

# Generate outline only (preview the structure before full expansion):
weave --outline-only

# Generate in English:
weave --language English

# Keep temp files for debugging:
weave --keep-temp

# Export as PDF (appended to pipeline)
weave --pdf

# If Gemini returns 503/high demand, wait longer before retrying
weave --unavailable-retry-delay 60 --max-retries 5

# Convert an existing Markdown file to PDF standalone
weave-pdf output/20260325_160828/handout.md
weave-pdf handout.md -o my_handout.pdf
```

You can also pass the API key directly:

```bash
weave -k "your-api-key" -i ./slides
```

## How It Works

### Two-Pass Prompting Strategy

1. **Pass 1 — Outline Generation**: All slide images are sent to the AI to generate a tree-structured chapter outline with page references. This gives the AI a bird's-eye view of the entire lecture.

2. **Pass 2 — Chapter Expansion**: Each chapter is expanded individually with its corresponding slide images AND the full outline as context. This ensures detailed, contextually-aware content while preserving every detail.

3. **Post-processing**: Referenced images are copied to the output folder, coverage is verified (ensuring no slide is missed), and temporary files are cleaned up.

## CLI Reference

See [docs/cli-reference.md](docs/cli-reference.md) for the full list of options and examples.

**Quick overview:**

| Command | Description |
|---------|-------------|
| `weave` | Full pipeline — PDF slides → Markdown handout |
| `weave --pdf` | Full pipeline + PDF export |
| `weave --outline-only` | Generate outline only (preview) |
| `weave-pdf <file.md>` | Convert an existing Markdown file to PDF |

## Output Structure

Each run creates a timestamped subfolder under the output directory:

```
output/
└── 20260325_160828/        # Timestamped folder (YYYYMMDD_HHMMSS)
    ├── handout.md          # The complete Markdown handout
    ├── handout.pdf          # PDF version (when --pdf is used)
    └── images/             # Embedded slide images (charts, diagrams, etc.)
        ├── slide_01_page_005.jpg
        ├── slide_01_page_012.jpg
        └── ...
```

## Programmatic Usage

Weave can also be used as a Python library. See [docs/programmatic-usage.md](docs/programmatic-usage.md) for details.

```python
from pathlib import Path
from weave import PipelineConfig, run_pipeline

config = PipelineConfig(
    input_dir=Path("./my-slides"),
    output_dir=Path("./my-notes"),
    temp_dir=Path("./tmp"),
    api_key="your-api-key",
    model="gemini-2.5-flash",
    language="English",
)

run_pipeline(config)
```

---

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for common issues and solutions.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
