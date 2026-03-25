"""Outline generation, parsing, and chapter expansion."""

import re

from google import genai

from ..config import PipelineConfig, console, progress_bar
from .client import call_gemini
from .prompts import get_expand_prompt, get_outline_prompt


def generate_outline(
    client: genai.Client,
    uploaded_files: dict[str, object],
    image_filenames: list[str],
    config: PipelineConfig,
) -> str:
    """Pass 1: Send all slides to generate a tree-structured outline."""
    console.print("[bold cyan]🗂️  Pass 1: Generating outline...[/]")

    contents: list = []
    for filename in image_filenames:
        contents.append(f"Slide {filename}:")
        contents.append(uploaded_files[filename])

    contents.append(
        "\n請根據以上所有投影片圖片，產出完整的樹狀章節大綱。"
        "務必標註每個小節對應的投影片檔名範圍，並標記含有圖表的頁面。"
        "確保每一頁投影片都至少被歸屬到一個章節中。"
    )

    outline = call_gemini(
        client,
        contents,
        system_instruction=get_outline_prompt(config.language),
        model=config.model,
        temperature=0.3,
    )

    console.print("[bold green]✓ Outline generated[/]\n")
    return outline


def parse_outline_chapters(outline: str) -> list[dict]:
    """Parse outline text into chapters with associated slide page references.

    Returns: [{title, outline_section, pages: [filename, ...]}, ...]
    """
    chapters: list[dict] = []
    current_chapter: str | None = None
    current_lines: list[str] = []
    current_pages: set[str] = set()

    page_pattern = re.compile(r"slide_\d{2}_page_\d{3}\.jpg")
    range_pattern = re.compile(
        r"slide_(\d{2})_page_(\d{3})\.jpg\s*~\s*slide_(\d{2})_page_(\d{3})\.jpg"
    )

    for line in outline.split("\n"):
        if re.match(r"^#{1,2}\s+", line) and not re.match(r"^#{3,}", line):
            if current_chapter and current_pages:
                chapters.append(
                    {
                        "title": current_chapter,
                        "outline_section": "\n".join(current_lines),
                        "pages": sorted(current_pages),
                    }
                )
            current_chapter = line.strip()
            current_lines = [line]
            current_pages = set()
        else:
            current_lines.append(line)

        for match in range_pattern.finditer(line):
            s_slide, s_page, e_slide, e_page = match.groups()
            if s_slide == e_slide:
                for p in range(int(s_page), int(e_page) + 1):
                    current_pages.add(f"slide_{s_slide}_page_{p:03d}.jpg")
            else:
                current_pages.add(f"slide_{s_slide}_page_{s_page}.jpg")
                current_pages.add(f"slide_{e_slide}_page_{e_page}.jpg")

        remaining = range_pattern.sub("", line)
        for single in page_pattern.finditer(remaining):
            current_pages.add(single.group())

    if current_chapter and current_pages:
        chapters.append(
            {
                "title": current_chapter,
                "outline_section": "\n".join(current_lines),
                "pages": sorted(current_pages),
            }
        )

    return chapters


def expand_chapter(
    client: genai.Client,
    chapter: dict,
    full_outline: str,
    uploaded_files: dict[str, object],
    config: PipelineConfig,
) -> str:
    """Pass 2: Expand a single chapter into detailed handout content."""
    contents: list = [
        "以下是完整的課程大綱，供你了解整體結構與前後脈絡：\n\n" + full_outline,
        "\n\n---\n你現在要擴寫的章節如下：\n" + chapter["outline_section"],
        "\n以下是該章節對應的投影片圖片：",
    ]

    for page in chapter["pages"]:
        if page in uploaded_files:
            contents.append(f"\n--- {page} ---")
            contents.append(uploaded_files[page])

    contents.append(
        "\n\n請根據以上投影片圖片和大綱，撰寫該章節的完整講義內容。"
        "確保不遺漏投影片中的任何資訊。"
        "若投影片中有重要圖表、公式或架構圖，"
        "請插入圖片引用 `![說明](./images/檔名.jpg)` 並提供詳細文字解析。"
    )

    return call_gemini(
        client,
        contents,
        system_instruction=get_expand_prompt(config.language),
        model=config.model,
        temperature=0.7,
    )


def expand_all_chapters(
    client: genai.Client,
    chapters: list[dict],
    full_outline: str,
    uploaded_files: dict[str, object],
    config: PipelineConfig,
) -> str:
    """Pass 2: Expand all chapters into a complete handout."""
    console.print("[bold cyan]📝 Pass 2: Expanding chapters...[/]")
    all_content: list[str] = []

    with progress_bar() as progress:
        task = progress.add_task("Expanding...", total=len(chapters))
        for i, chapter in enumerate(chapters, start=1):
            progress.update(task, description=f"Chapter {i}/{len(chapters)}...")
            content = expand_chapter(
                client, chapter, full_outline, uploaded_files, config
            )
            all_content.append(content)
            progress.update(task, advance=1)

    console.print("[bold green]✓ All chapters expanded[/]\n")
    return "\n\n---\n\n".join(all_content)
