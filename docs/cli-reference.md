# CLI Reference

## `weave` — Full Pipeline

Transform PDF lecture slides into structured Markdown handouts.

```bash
weave [OPTIONS]
```

### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` | `./data` | Input directory containing PDF files |
| `--output` | `-o` | `./output` | Output directory for handout and images |
| `--model` | `-m` | `gemini-2.5-flash` | Gemini model to use |
| `--api-key` | `-k` | `$GEMINI_API_KEY` | Gemini API key |
| `--dpi` | | `200` | DPI for PDF to image conversion |
| `--quality` | | `85` | JPEG quality (1–100) |
| `--language` | | `繁體中文` | Output language for the handout |
| `--temp-dir` | | `./temp` | Temporary directory for intermediate files |
| `--keep-temp` | | `false` | Keep temporary files after processing |
| `--outline-only` | | `false` | Only generate outline, skip expansion |
| `--pdf` | | `false` | Also export the handout as PDF |
| `--max-retries` | | `3` | Max Gemini retry attempts |
| `--retry-base-delay` | | `2` | Base retry delay in seconds for general API errors |
| `--unavailable-retry-delay` | | `30` | Minimum retry delay in seconds for Gemini `503 UNAVAILABLE` |
| `--version` | `-V` | | Show version number |

### Examples

```bash
# Basic — use defaults
weave

# Specify custom input / output directories
weave -i ./my-slides -o ./my-notes

# Use a higher-quality model
weave -m gemini-2.5-pro

# Preview the outline before full expansion
weave --outline-only

# Generate an English handout
weave --language English

# Full pipeline with PDF export
weave --pdf

# Keep temp files for debugging
weave --keep-temp

# Pass the API key directly
weave -k "your-api-key" -i ./slides

# Slow down retries when Gemini returns 503 high demand
weave --unavailable-retry-delay 60 --max-retries 5
```

---

## `weave-pdf` — Standalone Markdown → PDF

Convert an existing Markdown file to a styled PDF.

```bash
weave-pdf <input.md> [OPTIONS]
```

### Arguments & Options

| Argument / Option | Default | Description |
|-------------------|---------|-------------|
| `input` (positional) | — | Path to the `.md` file to convert |
| `--output` / `-o` | same dir, `.pdf` extension | Output PDF path |

### Examples

```bash
# Convert using default output path (handout.md → handout.pdf)
weave-pdf output/20260325_160828/handout.md

# Specify a custom output path
weave-pdf handout.md -o my_handout.pdf
```
