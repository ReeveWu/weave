"""Tests for outline parsing logic."""

from weave.ai.outline import parse_outline_chapters


def test_parse_single_chapter():
    outline = """\
# Chapter 1: Introduction
### 1.1 Overview [來源: slide_01_page_001.jpg ~ slide_01_page_003.jpg]
### 1.2 Goals [來源: slide_01_page_004.jpg]
"""
    chapters = parse_outline_chapters(outline)
    assert len(chapters) == 1
    assert chapters[0]["title"] == "# Chapter 1: Introduction"
    pages = chapters[0]["pages"]
    assert "slide_01_page_001.jpg" in pages
    assert "slide_01_page_002.jpg" in pages
    assert "slide_01_page_003.jpg" in pages
    assert "slide_01_page_004.jpg" in pages


def test_parse_multiple_chapters():
    outline = """\
# Chapter 1: Intro
### 1.1 Welcome [來源: slide_01_page_001.jpg]
## Chapter 2: Main Content
### 2.1 Core Concepts [來源: slide_01_page_002.jpg ~ slide_01_page_005.jpg]
### 2.2 Examples [來源: slide_01_page_006.jpg]
"""
    chapters = parse_outline_chapters(outline)
    assert len(chapters) == 2
    assert len(chapters[0]["pages"]) == 1
    assert "slide_01_page_001.jpg" in chapters[0]["pages"]
    assert "slide_01_page_002.jpg" in chapters[1]["pages"]
    assert "slide_01_page_005.jpg" in chapters[1]["pages"]
    assert "slide_01_page_006.jpg" in chapters[1]["pages"]


def test_parse_empty_outline():
    chapters = parse_outline_chapters("")
    assert chapters == []


def test_parse_no_page_references():
    outline = """\
# Chapter 1
### Section without page refs
Some text here.
"""
    chapters = parse_outline_chapters(outline)
    assert chapters == []


def test_parse_cross_file_range():
    outline = """\
# Combined Chapter
### Spanning files [來源: slide_01_page_010.jpg ~ slide_02_page_003.jpg]
"""
    chapters = parse_outline_chapters(outline)
    assert len(chapters) == 1
    pages = chapters[0]["pages"]
    assert "slide_01_page_010.jpg" in pages
    assert "slide_02_page_003.jpg" in pages


def test_parse_preserves_outline_section():
    outline = """\
# My Chapter
### 1.1 Part A [來源: slide_01_page_001.jpg]
### 1.2 Part B [來源: slide_01_page_002.jpg]
"""
    chapters = parse_outline_chapters(outline)
    assert "Part A" in chapters[0]["outline_section"]
    assert "Part B" in chapters[0]["outline_section"]
