"""PDF export from Markdown handout."""

from pathlib import Path

from ..config import PipelineConfig, console


def convert_md_to_pdf(md_path: Path, pdf_path: Path | None = None) -> Path:
    """Convert a Markdown file to PDF.

    Args:
        md_path: Path to the source ``.md`` file.
        pdf_path: Destination PDF path.  Defaults to the same directory /
                  same stem with a ``.pdf`` suffix.

    Returns:
        The resolved *pdf_path*.
    """
    import os
    import sys

    # On macOS with system Python, Homebrew's pango/gobject libraries are not on
    # the default library search path.  Setting DYLD_LIBRARY_PATH here (before
    # cffi/weasyprint calls dlopen) lets the dynamic linker resolve them.
    if sys.platform == "darwin":
        homebrew_lib = "/opt/homebrew/lib"
        if os.path.isdir(homebrew_lib):
            existing = os.environ.get("DYLD_LIBRARY_PATH", "")
            if homebrew_lib not in existing:
                os.environ["DYLD_LIBRARY_PATH"] = (
                    f"{homebrew_lib}:{existing}" if existing else homebrew_lib
                )

    import markdown
    from weasyprint import HTML

    md_path = Path(md_path).resolve()
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    if pdf_path is None:
        pdf_path = md_path.with_suffix(".pdf")
    else:
        pdf_path = Path(pdf_path).resolve()

    md_text = md_path.read_text(encoding="utf-8")

    extensions = ["tables", "fenced_code", "codehilite", "toc", "md_in_html"]
    html_body = markdown.markdown(md_text, extensions=extensions)

    # Wrap in full HTML with styling
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        font-family: "Helvetica Neue", Arial, "Noto Sans TC", "PingFang TC",
                     "Microsoft JhengHei", sans-serif;
        line-height: 1.8;
        max-width: 210mm;
        margin: 0 auto;
        padding: 20mm 15mm;
        color: #2c3e50;
        font-size: 11pt;
    }}
    h1 {{ font-size: 22pt; border-bottom: 2px solid #3498db; padding-bottom: 6px; margin-top: 30px; }}
    h2 {{ font-size: 17pt; border-bottom: 1px solid #bdc3c7; padding-bottom: 4px; margin-top: 24px; }}
    h3 {{ font-size: 14pt; margin-top: 18px; }}
    h4 {{ font-size: 12pt; margin-top: 14px; }}
    code {{
        background-color: #f4f4f4;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 10pt;
    }}
    pre {{
        background-color: #f4f4f4;
        padding: 12px;
        border-radius: 5px;
        overflow-x: auto;
        font-size: 10pt;
        line-height: 1.4;
    }}
    pre code {{ background: none; padding: 0; }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
    }}
    th, td {{
        border: 1px solid #ddd;
        padding: 8px 12px;
        text-align: left;
    }}
    th {{ background-color: #3498db; color: white; }}
    tr:nth-child(even) {{ background-color: #f9f9f9; }}
    img {{
        max-width: 100%;
        height: auto;
        display: block;
        margin: 10px auto;
    }}
    blockquote {{
        border-left: 4px solid #3498db;
        margin: 12px 0;
        padding: 8px 16px;
        background-color: #f0f7fd;
        color: #555;
    }}
    hr {{ border: none; border-top: 1px solid #ddd; margin: 24px 0; }}
    ul, ol {{ padding-left: 24px; }}
    li {{ margin-bottom: 4px; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # Use base_url so relative image paths resolve correctly
    HTML(
        string=html_content,
        base_url=str(md_path.parent),
    ).write_pdf(str(pdf_path))

    return pdf_path


def convert_to_pdf(config: PipelineConfig) -> None:
    """Convert the generated Markdown handout to PDF (pipeline integration)."""
    md_path = config.output_dir / "handout.md"
    console.print("[bold cyan]📑 Converting Markdown to PDF...[/]")
    pdf_path = convert_md_to_pdf(md_path)
    console.print(f"[bold green]✓ PDF saved to {pdf_path}[/]")
