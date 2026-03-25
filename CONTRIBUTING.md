# Contributing to Weave

Thank you for your interest in contributing! Here's how you can help.

## Getting Started

```bash
# Fork and clone
git clone https://github.com/ReeveWu/weave.git
cd weave

# Install with dev dependencies
pip install -e ".[dev]"
```

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run linting: `ruff check .`
4. Run tests: `pytest`
5. Commit with a clear message: `git commit -m "feat(xxx): add X feature"`
6. Push and open a Pull Request

## Commit Message Convention

- `feat(xxx):` — New feature
- `fix(xxx):` — Bug fix
- `docs(xxx):` — Documentation changes
- `refactor(xxx):` — Code refactoring
- `test(xxx):` — Adding or updating tests
- `chore(xxx):` — Maintenance tasks

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions
- Use [Ruff](https://docs.astral.sh/ruff/) for linting: `ruff check .`
- Type hints are encouraged for function signatures
- Keep functions focused and well-named

## Areas for Contribution

- **New LLM providers** — Add support for OpenAI, Anthropic, or local models
- **Output formats** — PDF export, HTML, EPUB
- **Input formats** — PPTX support, image folders
- **Prompt improvements** — Better prompts for specific subjects (math, CS, humanities)
- **i18n** — Improved multi-language prompt templates
- **Tests** — Expand test coverage
- **Documentation** — Tutorials, examples, translations

## Reporting Issues

When reporting a bug, please include:

1. Python version (`python --version`)
2. OS and version
3. Steps to reproduce
4. Expected vs actual behavior
5. Error messages or logs
