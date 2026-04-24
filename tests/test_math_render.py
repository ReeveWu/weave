"""Tests for lightweight LaTeX math rendering."""

from weave.export.math_render import latex_to_html, protect_math


def test_latex_to_html_uses_block_safe_span_for_display_math():
    rendered = latex_to_html(r"R^2 = \frac{SS_{explained}}{SS_{total}}", display=True)

    assert rendered.startswith('<span class="math-display">')
    assert '<span class="mfrac">' in rendered


def test_protect_math_treats_single_dollar_line_as_display_math():
    text, mapping = protect_math("$R^2 = \\frac{SS_{explained}}{SS_{total}}$")

    assert text == "MTHPH00001"
    assert 'class="math-display"' in mapping["MTHPH00001"]
    assert "R<sup>2</sup>" in mapping["MTHPH00001"]


def test_protect_math_keeps_embedded_single_dollar_math_inline():
    text, mapping = protect_math(
        "最終，$R^2 = \\frac{SS_{explained}}{SS_{total}}$ 與公式一致。"
    )

    assert text == "最終，MTHPH00001 與公式一致。"
    assert 'class="math-inline"' in mapping["MTHPH00001"]
