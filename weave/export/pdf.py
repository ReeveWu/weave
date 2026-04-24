"""PDF export from Markdown handout."""

from pathlib import Path

from ..config import PipelineConfig, console
from .postprocess import (
    _ensure_list_spacing,
    _ensure_table_spacing,
    _unwrap_backtick_images,
)


def _get_code_css() -> str:
    """Return Pygments CSS plus PDF-friendly wrapping for highlighted code."""
    from pygments.formatters import HtmlFormatter

    pygments_css = HtmlFormatter(style="friendly").get_style_defs(".codehilite")
    return f"""
{pygments_css}

    /* --- Code block rendering --- */
    .codehilite {{
        background-color: #f4f4f4;
        border-radius: 5px;
        margin: 12px 0;
        max-width: 100%;
    }}
    .codehilite pre {{
        margin: 0;
    }}
    .codehilite pre,
    .codehilite code {{
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        word-break: break-word;
    }}
    .codehilite code {{
        display: block;
        background: transparent;
        padding: 0;
        border-radius: 0;
        color: inherit;
    }}
"""


def _markdown_to_html(md_text: str) -> str:
    """Convert Markdown to HTML with protected math and Pygments code classes."""
    import markdown

    from .math_render import protect_math, restore_math

    md_text = _ensure_list_spacing(md_text)
    md_text = _ensure_table_spacing(md_text)
    md_text = _unwrap_backtick_images(md_text)

    # Protect $...$ math from Markdown mangling (_ as emphasis, etc.)
    md_text, math_map = protect_math(md_text)

    extensions = ["tables", "fenced_code", "codehilite", "toc", "md_in_html"]
    extension_configs = {
        "codehilite": {
            "guess_lang": False,
            "linenums": False,
            "noclasses": False,
            "use_pygments": True,
        }
    }
    html_body = markdown.markdown(
        md_text,
        extensions=extensions,
        extension_configs=extension_configs,
    )

    return restore_math(html_body, math_map)


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

    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration

    from .math_render import MATH_CSS

    md_path = Path(md_path).resolve()
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    if pdf_path is None:
        pdf_path = md_path.with_suffix(".pdf")
    else:
        pdf_path = Path(pdf_path).resolve()

    html_body = _markdown_to_html(md_path.read_text(encoding="utf-8"))
    code_css = _get_code_css()

    font_config = FontConfiguration()

    # Wrap in full HTML with styling
    # NOTE: macOS Preview has rendering issues with CFF-based OpenType fonts
    # (CID Type 0C) like PingFang TC.  TrueType-based CJK fonts such as
    # "Heiti TC" embed as CID TrueType and render correctly in Preview.
    # Chrome's PDF viewer (PDFium) handles both formats fine, which is why
    # the PDF looks correct in Chrome but has missing glyphs in Preview.
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        font-family: "Heiti TC", "Noto Sans TC", "Microsoft JhengHei",
                     "PingFang TC", "Helvetica Neue", Arial, sans-serif;
        line-height: 1.8;
        max-width: 210mm;
        margin: 0 auto;
        padding: 20mm 15mm;
        color: #2c3e50;
        font-size: 11pt;
    }}
    h1 {{
        font-size: 22pt;
        border-bottom: 2px solid #3498db;
        padding-bottom: 6px;
        margin-top: 30px;
    }}
    h2 {{
        font-size: 17pt;
        border-bottom: 1px solid #bdc3c7;
        padding-bottom: 4px;
        margin-top: 24px;
    }}
    h3 {{ font-size: 14pt; margin-top: 18px; }}
    h4 {{ font-size: 12pt; margin-top: 14px; }}
    code {{
        background-color: #f4f4f4;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 10pt;
        font-family: "Heiti TC", "Noto Sans TC", "Microsoft JhengHei",
                     Menlo, Consolas, "Courier New", monospace;
    }}
    pre {{
        background-color: #f4f4f4;
        padding: 12px;
        border-radius: 5px;
        overflow-x: auto;
        font-size: 10pt;
        line-height: 1.4;
        font-family: "Heiti TC", "Noto Sans TC", "Microsoft JhengHei",
                     Menlo, Consolas, "Courier New", monospace;
    }}
    pre code {{ background: none; padding: 0; }}
{code_css}
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
{MATH_CSS}
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
    ).write_pdf(str(pdf_path), font_config=font_config)

    return pdf_path


def convert_to_pdf(config: PipelineConfig) -> None:
    """Convert the generated Markdown handout to PDF (pipeline integration)."""
    md_path = config.output_dir / "handout.md"
    console.print("[bold cyan]📑 Converting Markdown to PDF...[/]")
    pdf_path = convert_md_to_pdf(md_path)
    console.print(f"[bold green]✓ PDF saved to {pdf_path}[/]")
