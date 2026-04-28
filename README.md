<div align="center">

<div style="margin: 20px 0;">
  <img src="./assets/logo.png" height="60" alt="Weave Logo" >
</div>

# Weave

**Weave your lecture slides into comprehensive, structured Markdown handouts with AI.**

*Never miss a detail from your lecture slides again.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-339933.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg)](https://ai.google.dev/)

[English](#features) | [繁體中文](README.zh.md)

</div>

---

Weave is an AI-powered tool that transforms PDF slides into structured Markdown study guides. It offers a **modern web interface** for point-and-click usage, as well as a **CLI** for scripting and automation.

## Features

- **Two-Pass AI Analysis** — First generates a structured outline, then expands each chapter with full context
- **PDF to Handout** — Converts multi-page PDF slides into a single, well-organized Markdown document
- **Smart Image Embedding** — Automatically identifies and embeds important charts, diagrams, and formulas
- **Coverage Verification** — Ensures every single slide page is referenced in the final handout
- **Multi-language Output** — Generate handouts in any language (default: Traditional Chinese)
- **Zero Content Loss** — Preserves ALL information from slides, including footnotes and small annotations
- **PDF Export** — One command to convert Markdown handouts to beautifully styled PDFs
- **Powered by Gemini** — Leverages Google's multimodal AI with large context window

---

## Quick Start (Web UI)

### Prerequisites

- **Python 3.10+** and **Node.js 18+**
- [Poppler](https://poppler.freedesktop.org/) — required for PDF rendering
- [Pango](https://www.gtk.org/docs/architecture/pango) — required for PDF export
- A [Google Gemini API key](https://aistudio.google.com/apikey)

```bash
# macOS
brew install poppler pango

# Ubuntu / Debian
sudo apt-get install poppler-utils libpango-1.0-0 libpangoft2-1.0-0
```

### 1. Clone the repository

```bash
git clone https://github.com/ReeveWu/weave.git
cd weave
```

### 2. Install dependencies

Run this once to set up the Python virtual environment and install all dependencies:

```bash
npm run setup
```

This command:
- Creates a Python virtual environment at `.venv/`
- Installs the `weave` Python package and all server dependencies
- Installs frontend (`client/`) npm packages

### 3. Start the application

```bash
npm run start
```

This launches both servers concurrently:
- **Backend API** at `http://localhost:8000`
- **Web UI** at `http://localhost:3000`

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Using the Web UI

1. **Upload PDFs** — Drag and drop (or click to browse) one or more PDF slide files
2. **Configure** — Enter your Gemini API key, choose a model and output language, optionally enable PDF export
3. **Run** — Click **Start** and watch real-time progress across each pipeline stage
4. **Get results** — View the rendered Markdown handout, then copy, download, or export as PDF

---

## Alternative: CLI Usage

> The CLI is ideal for scripting, automation, or batch processing. It requires the Python environment to be set up (see above).

Activate the virtual environment first:

```bash
source .venv/bin/activate
```

Place your PDF slides in `./data/`, then:

```bash
# Full pipeline — PDF slides → Markdown handout
weave

# Specify custom input/output directories
weave -i ./my-slides -o ./my-notes

# Use a specific model
weave -m gemini-2.5-pro

# Generate outline only (preview the structure before full expansion)
weave --outline-only

# Generate in English
weave --language English

# Full pipeline + PDF export
weave --pdf

# Pass API key directly (no .env file needed)
weave -k "your-api-key" -i ./slides

# If Gemini returns 503 / high demand, increase retry patience
weave --unavailable-retry-delay 60 --max-retries 6

# Convert an existing Markdown file to PDF standalone
weave-pdf output/20260325_160828/handout.md
weave-pdf handout.md -o my_handout.pdf
```

#### CLI environment setup

For the CLI, you can set your API key via `.env` instead of passing `-k` each time:

```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_actual_key
```

See [docs/cli-reference.md](docs/cli-reference.md) for the full list of options.

---

## How It Works

### Two-Pass Prompting Strategy

1. **Pass 1 — Outline Generation**: All slide images are sent to the AI to produce a tree-structured chapter outline with page references. This gives the AI a bird's-eye view of the entire lecture.

2. **Pass 2 — Chapter Expansion**: Each chapter is expanded individually with its corresponding slide images **and** the full outline as context. This ensures detailed, contextually-aware content while preserving every detail.

3. **Post-processing**: Referenced images are copied to the output folder, coverage is verified (ensuring no slide is missed), and temporary files are cleaned up.

## Output Structure

Each run creates a timestamped subfolder under the output directory:

```
output/
└── 20260325_160828/        # Timestamped folder (YYYYMMDD_HHMMSS)
    ├── handout.md          # The complete Markdown handout
    ├── handout.pdf         # PDF version (when PDF export is enabled)
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
