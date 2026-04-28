"""Tests for Markdown-to-PDF HTML preparation."""

from weave.export.pdf import _get_code_css, _markdown_to_html


def test_markdown_to_html_highlights_python_fenced_code():
    html = _markdown_to_html(
        """```python
from sklearn.linear_model import LinearRegression
model = LinearRegression(fit_intercept=True)
```"""
    )

    assert 'class="codehilite"' in html
    assert 'class="kn"' in html
    assert 'class="nn"' in html


def test_code_css_wraps_long_lines_for_pdf():
    css = _get_code_css()

    assert ".codehilite" in css
    assert "white-space: pre-wrap" in css
    assert "overflow-wrap: anywhere" in css


def test_markdown_to_html_preserves_bold_list_heading_break():
    html = _markdown_to_html(
        """*   **決策樹：不同準確度層級**
    決策樹是一種機器學習模型。"""
    )

    assert "<strong>決策樹：不同準確度層級</strong><br" in html
