"""Tests for Markdown post-processing helpers."""

from weave.export.postprocess import _ensure_list_spacing


def test_ensure_list_spacing_handles_nested_list_items_after_paragraphs():
    markdown = """\
*   **所有樹運行後的鄰近矩陣**：
    最終，將所有資料運行通過森林中的所有決策樹後，鄰近矩陣將被完整填寫並正規化。

    鄰近矩陣的每個元素 `P[i,j]` 表示樣本 `i` 和樣本 `j` 在所有樹中落入相同葉節點的次數。
    *   例如，`P[3,4] = 8` 表示樣本 3 和樣本 4 在 10 棵樹中有 8 棵樹中落入相同的葉節點。
    *   對角線元素 `P[i,i]` 通常表示樣本 `i` 在所有樹中落入葉節點的總次數。
"""

    result = _ensure_list_spacing(markdown)

    assert (
        "葉節點的次數。\n\n    *   例如，`P[3,4] = 8` 表示樣本 3 和樣本 4"
    ) in result
    assert ("相同的葉節點。\n    *   對角線元素 `P[i,i]` 通常表示樣本 `i`") in result


def test_ensure_list_spacing_handles_ordered_markers_beyond_one():
    markdown = "Intro\n2. second"

    assert _ensure_list_spacing(markdown) == "Intro\n\n2. second"


def test_ensure_list_spacing_ignores_fenced_code_blocks():
    markdown = """\
```md
Intro
* not a real list
```
"""

    assert _ensure_list_spacing(markdown) == markdown.rstrip("\n")
