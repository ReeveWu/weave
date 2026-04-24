"""Convert LaTeX math notation ($...$) to styled HTML for WeasyPrint."""

import html
import re

# ---------------------------------------------------------------------------
# LaTeX symbol → Unicode mapping
# ---------------------------------------------------------------------------
_SYMBOLS: dict[str, str] = {
    # Comparison & arithmetic
    r"\ge": "≥",
    r"\geq": "≥",
    r"\le": "≤",
    r"\leq": "≤",
    r"\ne": "≠",
    r"\neq": "≠",
    r"\approx": "≈",
    r"\sim": "∼",
    r"\times": "×",
    r"\cdot": "·",
    r"\pm": "±",
    r"\mp": "∓",
    r"\div": "÷",
    # Big operators
    r"\sum": "∑",
    r"\prod": "∏",
    r"\int": "∫",
    r"\partial": "∂",
    r"\nabla": "∇",
    r"\infty": "∞",
    # Greek lowercase
    r"\alpha": "α",
    r"\beta": "β",
    r"\gamma": "γ",
    r"\delta": "δ",
    r"\epsilon": "ε",
    r"\varepsilon": "ε",
    r"\zeta": "ζ",
    r"\eta": "η",
    r"\theta": "θ",
    r"\iota": "ι",
    r"\kappa": "κ",
    r"\lambda": "λ",
    r"\mu": "μ",
    r"\nu": "ν",
    r"\xi": "ξ",
    r"\pi": "π",
    r"\rho": "ρ",
    r"\sigma": "σ",
    r"\tau": "τ",
    r"\upsilon": "υ",
    r"\phi": "φ",
    r"\varphi": "φ",
    r"\chi": "χ",
    r"\psi": "ψ",
    r"\omega": "ω",
    # Greek uppercase
    r"\Gamma": "Γ",
    r"\Delta": "Δ",
    r"\Theta": "Θ",
    r"\Lambda": "Λ",
    r"\Xi": "Ξ",
    r"\Pi": "Π",
    r"\Sigma": "Σ",
    r"\Phi": "Φ",
    r"\Psi": "Ψ",
    r"\Omega": "Ω",
    # Set & logic
    r"\in": "∈",
    r"\notin": "∉",
    r"\subset": "⊂",
    r"\supset": "⊃",
    r"\subseteq": "⊆",
    r"\supseteq": "⊇",
    r"\cup": "∪",
    r"\cap": "∩",
    r"\forall": "∀",
    r"\exists": "∃",
    r"\neg": "¬",
    r"\land": "∧",
    r"\lor": "∨",
    # Arrows
    r"\leftarrow": "←",
    r"\rightarrow": "→",
    r"\leftrightarrow": "↔",
    r"\Leftarrow": "⇐",
    r"\Rightarrow": "⇒",
    r"\Leftrightarrow": "⇔",
    # Dots
    r"\ldots": "…",
    r"\cdots": "⋯",
    r"\dots": "…",
    # Spacing (collapsed to thin spaces for PDF)
    r"\quad": "\u2003",
    r"\qquad": "\u2003\u2003",
    r"\,": "\u2009",
    r"\;": "\u2005",
    r"\!": "",
}

# ---------------------------------------------------------------------------
# Low-level LaTeX parsing helpers
# ---------------------------------------------------------------------------


def _parse_group(latex: str, pos: int) -> tuple[str, int]:
    """Parse ``{...}`` starting at ``{``.  Returns *(content, new_pos)*."""
    depth = 1
    start = pos + 1
    pos += 1
    while pos < len(latex) and depth > 0:
        if latex[pos] == "{":
            depth += 1
        elif latex[pos] == "}":
            depth -= 1
        pos += 1
    return latex[start : pos - 1], pos


def _parse_arg(latex: str, pos: int) -> tuple[str, int]:
    """Parse one argument — either ``{group}`` or a single character."""
    if pos >= len(latex):
        return "", pos
    if latex[pos] == "{":
        return _parse_group(latex, pos)
    return latex[pos], pos + 1


def _parse_command(latex: str, pos: int) -> tuple[str, int]:
    r"""Parse ``\command`` starting at ``\``.

    Returns *(cmd_with_backslash, new_pos)*.
    """
    pos += 1  # skip '\'
    if pos >= len(latex):
        return "\\", pos
    if not latex[pos].isalpha():
        return "\\" + latex[pos], pos + 1
    start = pos
    while pos < len(latex) and latex[pos].isalpha():
        pos += 1
    return "\\" + latex[start:pos], pos


# ---------------------------------------------------------------------------
# Core converter
# ---------------------------------------------------------------------------


def _convert(latex: str) -> str:
    """Recursively convert a LaTeX math expression to HTML tokens."""
    result: list[str] = []
    pos = 0
    n = len(latex)

    while pos < n:
        ch = latex[pos]

        # ----- backslash commands -----
        if ch == "\\":
            cmd, new_pos = _parse_command(latex, pos)

            if cmd in _SYMBOLS:
                result.append(_SYMBOLS[cmd])
                pos = new_pos

            elif cmd == r"\frac":
                num, pos = _parse_arg(latex, new_pos)
                den, pos = _parse_arg(latex, pos)
                result.append(
                    '<span class="mfrac">'
                    f'<span class="mfrac-num">{_convert(num)}</span>'
                    f'<span class="mfrac-den">{_convert(den)}</span>'
                    "</span>"
                )

            elif cmd == r"\sqrt":
                arg, pos = _parse_arg(latex, new_pos)
                result.append(
                    f'√<span style="text-decoration:overline">{_convert(arg)}</span>'
                )

            elif cmd == r"\hat":
                arg, pos = _parse_arg(latex, new_pos)
                result.append(f"{_convert(arg)}\u0302")

            elif cmd == r"\bar":
                arg, pos = _parse_arg(latex, new_pos)
                result.append(f"{_convert(arg)}\u0304")

            elif cmd == r"\overline":
                arg, pos = _parse_arg(latex, new_pos)
                result.append(
                    f'<span style="text-decoration:overline">{_convert(arg)}</span>'
                )

            elif cmd in (r"\mathbf", r"\boldsymbol", r"\bf"):
                arg, pos = _parse_arg(latex, new_pos)
                result.append(f"<strong>{_convert(arg)}</strong>")

            elif cmd in (r"\mathrm", r"\text", r"\textrm", r"\mbox"):
                arg, pos = _parse_arg(latex, new_pos)
                result.append(f'<span style="font-style:normal">{_convert(arg)}</span>')

            elif cmd in (r"\left", r"\right", r"\big", r"\Big", r"\bigg", r"\Bigg"):
                # sizing hints — just skip the command itself
                pos = new_pos

            else:
                # Unknown command — render name in normal style
                result.append(html.escape(cmd))
                pos = new_pos

        # ----- superscript -----
        elif ch == "^":
            pos += 1
            arg, pos = _parse_arg(latex, pos)
            result.append(f"<sup>{_convert(arg)}</sup>")

        # ----- subscript -----
        elif ch == "_":
            pos += 1
            arg, pos = _parse_arg(latex, pos)
            result.append(f"<sub>{_convert(arg)}</sub>")

        # ----- braces (group) -----
        elif ch == "{":
            content, pos = _parse_group(latex, pos)
            result.append(_convert(content))

        elif ch == "}":
            pos += 1  # stray closing brace

        # ----- tilde = non-breaking space -----
        elif ch == "~":
            result.append("&nbsp;")
            pos += 1

        # ----- HTML-sensitive chars -----
        elif ch in "<>&":
            result.append(html.escape(ch))
            pos += 1

        # ----- everything else (digits, letters, operators, parens …) -----
        else:
            result.append(ch)
            pos += 1

    return "".join(result)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def latex_to_html(latex: str, *, display: bool = False) -> str:
    """Convert a LaTeX expression (without ``$`` delimiters) to HTML."""
    inner = _convert(latex.strip())
    if display:
        return f'<span class="math-display">{inner}</span>'
    return f'<span class="math-inline">{inner}</span>'


# Placeholder prefix — chosen to be unlikely in normal text
_PH_PREFIX = "MTHPH"


def protect_math(md_text: str) -> tuple[str, dict[str, str]]:
    """Replace ``$$…$$`` and ``$…$`` with placeholders before Markdown parsing.

    Returns *(processed_text, {placeholder: html})*  so that the Markdown
    engine does not mangle underscores / asterisks inside math.
    """
    mapping: dict[str, str] = {}
    counter = [0]

    def _repl(m: re.Match, display: bool) -> str:
        counter[0] += 1
        key = f"{_PH_PREFIX}{counter[0]:05d}"
        raw = m.group(1)
        mapping[key] = latex_to_html(raw, display=display)
        return key

    def _line_repl(m: re.Match) -> str:
        counter[0] += 1
        key = f"{_PH_PREFIX}{counter[0]:05d}"
        mapping[key] = latex_to_html(m.group(2), display=True)
        return f"{m.group(1)}{key}"

    # Display math first (greedy $$…$$), then single-dollar equations that
    # occupy a whole line.  LLMs often emit display equations as plain $...$.
    text = re.sub(r"\$\$(.+?)\$\$", lambda m: _repl(m, True), md_text, flags=re.DOTALL)
    text = re.sub(
        r"(?m)^([ \t]*(?:(?:[-*+]|\d+[.)])[ \t]+)?)\$([^\$\n]+?)\$[ \t]*$",
        _line_repl,
        text,
    )
    text = re.sub(r"(?<!\$)\$([^\$\n]+?)\$(?!\$)", lambda m: _repl(m, False), text)
    return text, mapping


def restore_math(html_text: str, mapping: dict[str, str]) -> str:
    """Replace placeholders in the HTML output with rendered math HTML."""
    for key, rendered in mapping.items():
        # The placeholder may have been HTML-escaped by the Markdown engine
        html_text = html_text.replace(html.escape(key), rendered)
        html_text = html_text.replace(key, rendered)
    return html_text


# ---------------------------------------------------------------------------
# CSS injected into the PDF template
# ---------------------------------------------------------------------------

MATH_CSS = """
    /* --- Math rendering --- */
    .math-inline {
        font-style: italic;
        overflow-wrap: anywhere;
        white-space: normal;
    }
    .math-display {
        font-style: italic;
        display: block;
        text-align: center;
        margin: 10px auto;
        max-width: 100%;
        overflow-wrap: anywhere;
        white-space: normal;
    }
    .math-inline strong, .math-display strong {
        font-style: normal;
    }
    .mfrac {
        display: inline-block;
        text-align: center;
        vertical-align: -0.45em;
        white-space: nowrap;
        line-height: 1;
        margin: 0 2px;
    }
    .mfrac-num {
        display: block;
        border-bottom: 1px solid currentColor;
        padding: 0 3px 1px;
        line-height: 1.2;
    }
    .mfrac-den {
        display: block;
        padding: 1px 3px 0;
        line-height: 1.2;
    }
"""
