"""Post-processing: image copying, handout saving, coverage verification."""

import re
import shutil

from ..config import PipelineConfig, console


def _ensure_list_spacing(md_text: str) -> str:
    list_item_re = re.compile(r"^[ \t]*(?:[*+-]|\d+[.)])[ \t]+")
    fence_re = re.compile(r"^\s{0,3}(```|~~~)")
    text = md_text.splitlines()
    result = []
    in_fence = False
    for i, line in enumerate(text):
        if fence_re.match(line):
            in_fence = not in_fence

        prev = text[i - 1] if i > 0 else ""
        if (
            not in_fence
            and list_item_re.match(line)
            and i > 0
            and not list_item_re.match(prev)
            and prev.strip() != ""
        ):
            result.append("")
        result.append(line)
    return "\n".join(result)


def _ensure_list_heading_breaks(md_text: str) -> str:
    """Preserve line breaks after bold-only list item headings.

    Markdown treats an indented continuation line as part of the same paragraph,
    so HTML collapses the source newline into a single space.  A trailing two
    spaces turns the author-intended break into a Markdown hard break.
    """
    list_item_re = re.compile(r"^[ \t]*(?:[*+-]|\d+[.)])[ \t]+")
    bold_heading_re = re.compile(
        r"^[ \t]*(?:[*+-]|\d+[.)])[ \t]+(?:\*\*.+\*\*|__.+__)[ \t]*$"
    )
    fence_re = re.compile(r"^\s{0,3}(```|~~~)")
    lines = md_text.splitlines()
    result: list[str] = []
    in_fence = False

    for i, line in enumerate(lines):
        if fence_re.match(line):
            in_fence = not in_fence

        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        has_indented_continuation = (
            next_line.startswith((" ", "\t"))
            and next_line.strip() != ""
            and not list_item_re.match(next_line)
        )
        if (
            not in_fence
            and bold_heading_re.match(line)
            and has_indented_continuation
            and not line.endswith(("  ", "\\"))
        ):
            line = f"{line.rstrip()}  "
        result.append(line)

    return "\n".join(result)


def _unwrap_backtick_images(md_text: str) -> str:
    """Remove backticks wrapping image references so they render as images.

    Converts  `![alt](path)`  →  ![alt](path)
    """
    return re.sub(r"`(!\[.*?\]\(.*?\))`", r"\1", md_text)


def _ensure_table_spacing(md_text: str) -> str:
    """Insert a blank line before table blocks that lack one.

    Markdown parsers require a blank line before a table; without it the
    ``| … |`` rows are rendered as plain text.
    """
    lines = md_text.splitlines()
    result: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        prev = lines[i - 1] if i > 0 else ""
        prev_stripped = prev.lstrip()
        if (
            stripped.startswith("|")
            and i > 0
            and not prev_stripped.startswith("|")
            and prev.strip() != ""
        ):
            result.append("")
        result.append(line)
    return "\n".join(result)


def post_process(
    markdown_content: str,
    all_image_filenames: list[str],
    config: PipelineConfig,
) -> None:
    """Copy referenced images, save handout, and verify slide coverage."""
    console.print("[bold cyan]🔧 Post-processing...[/]")

    markdown_content = _ensure_list_spacing(markdown_content)
    markdown_content = _ensure_list_heading_breaks(markdown_content)
    markdown_content = _ensure_table_spacing(markdown_content)
    markdown_content = _unwrap_backtick_images(markdown_content)

    # 1. Find referenced images in the Markdown
    ref_pattern = re.compile(r"!\[.*?\]\(\./images/(slide_\d{2}_page_\d{3}\.jpg)\)")
    referenced = set(ref_pattern.findall(markdown_content))

    # 2. Copy referenced images to output
    copied = 0
    for img in referenced:
        src = config.temp_dir / img
        if src.exists():
            shutil.copy2(str(src), str(config.images_dir / img))
            copied += 1
        else:
            console.print(f"[yellow]  Warning: Referenced image {img} not found[/]")

    console.print(f"  📎 Copied {copied} referenced images to output/images/")

    # 3. Save the final Markdown
    output_path = config.output_dir / "handout.md"
    output_path.write_text(markdown_content, encoding="utf-8")
    console.print(f"  📄 Handout saved to {output_path}")

    # 4. Coverage verification
    all_set = set(all_image_filenames)
    page_re = re.compile(r"slide_\d{2}_page_\d{3}\.jpg")
    mentioned = set(page_re.findall(markdown_content))
    missing = all_set - mentioned

    if missing:
        console.print(
            f"\n[yellow]  ⚠ {len(missing)} slide(s) not mentioned in handout:[/]"
        )
        for p in sorted(missing):
            console.print(f"    [dim]{p}[/]")
    else:
        console.print("  [green]✓ All slides covered[/]")
