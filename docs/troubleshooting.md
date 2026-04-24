# Troubleshooting

## macOS: `cannot load library 'libgobject-2.0-0'` during PDF export

When using the macOS system Python, Homebrew-installed libraries such as pango and gobject are not on the default dynamic library search path.

Weave automatically prepends `/opt/homebrew/lib` to `DYLD_LIBRARY_PATH` at runtime, so this should work out of the box in most cases.

If you still see the error, add the following to your `~/.zshrc` (or `~/.bashrc`):

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
```

Then reload your shell:

```bash
source ~/.zshrc
```

## Missing system dependencies

WeasyPrint requires system-level libraries for rendering. Make sure you have installed the prerequisites:

```bash
# macOS
brew install poppler pango

# Ubuntu / Debian
sudo apt-get install poppler-utils libpango-1.0-0 libpangoft2-1.0-0
```

For Windows or other platforms, see the [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

## Gemini API key not found

Weave looks for an API key in this order:

1. `--api-key` / `-k` CLI flag
2. `GEMINI_API_KEY` environment variable
3. `.env` file in the current directory

Make sure at least one of these is set:

```bash
# Option A — .env file
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key

# Option B — environment variable
export GEMINI_API_KEY="your_key"

# Option C — CLI flag
weave -k "your_key"
```

## Gemini API returns `503 UNAVAILABLE`

Gemini may temporarily return `503 UNAVAILABLE` when the selected model is under high demand.

Weave now waits longer for that specific error before retrying. You can tune the behavior with either CLI flags or environment variables:

```bash
# Example: wait at least 60 seconds for 503, and retry up to 6 times
weave --unavailable-retry-delay 60 --max-retries 6

# Equivalent env vars
export WEAVE_UNAVAILABLE_RETRY_DELAY=60
export WEAVE_MAX_RETRIES=6
```

For ordinary API errors, the general backoff is controlled by `--retry-base-delay` or `WEAVE_RETRY_BASE_DELAY`.
