# Programmatic Usage

You can use Weave as a Python library in addition to the CLI.

## Basic Pipeline

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

A timestamped subfolder (e.g. `my-notes/20260325_160828/`) will be created automatically.

## Standalone Markdown → PDF

```python
from pathlib import Path
from weave.export.pdf import convert_md_to_pdf

pdf_path = convert_md_to_pdf(
    md_path=Path("output/20260325_160828/handout.md"),
    # pdf_path is optional; defaults to handout.pdf in the same directory
)
print(f"PDF saved to {pdf_path}")
```

## Configuration Options

`PipelineConfig` accepts the following fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `input_dir` | `Path` | — | Directory containing PDF slides |
| `output_dir` | `Path` | — | Base output directory |
| `temp_dir` | `Path` | — | Temporary directory for intermediate files |
| `model` | `str` | `"gemini-2.5-flash"` | Gemini model name |
| `api_key` | `str` | — | Gemini API key |
| `dpi` | `int` | `200` | DPI for PDF → image conversion |
| `quality` | `int` | `85` | JPEG quality (1–100) |
| `language` | `str` | `"繁體中文"` | Output language |
| `keep_temp` | `bool` | `False` | Keep temporary files |
| `outline_only` | `bool` | `False` | Only generate outline |
| `pdf` | `bool` | `False` | Export handout as PDF |
| `max_retries` | `int` | `6` | Max Gemini retry attempts |
| `retry_base_delay` | `int` | `2` | Base retry delay in seconds for general API errors |
| `unavailable_retry_delay` | `int` | `30` | Minimum retry delay in seconds for Gemini `503 UNAVAILABLE` |
