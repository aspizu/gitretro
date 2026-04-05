# gitretro

Generate a retrospective of changes in a git repository using LLMs.

`gitretro` analyzes the diff between two commits and uses Google Gemini to produce a concise, human-readable retrospective for each changed file. Retrospectives are rendered as an [mdbook](https://rust-lang.github.io/mdBook/) and can be served locally in your browser.

## Features

- Per-file AI-generated summaries focused on architectural intent, not line-by-line noise
- Multi-account Gemini API key rotation with automatic rate-limit handling and retry
- Retrospectives stored locally as mdbook projects under `.gitretro/`
- List all previously generated retrospectives with commit context

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv)
- [mdbook](https://rust-lang.github.io/mdBook/) (must be on `PATH`)
- One or more [Google Gemini API keys](https://aistudio.google.com/app/apikey)

## Installation

```sh
uv tool install gitretro
```

## Configuration

Create `~/.config/gitretro/config.toml`:

```toml
[[accounts]]
email = "you@example.com"
api_key = "YOUR_GEMINI_API_KEY"

# Add more accounts for automatic key rotation:
[[accounts]]
email = "alt@example.com"
api_key = "ANOTHER_GEMINI_API_KEY"
```

Multiple accounts are cycled automatically when a key hits its rate limit.

## Usage

### Generate a retrospective

```sh
gitretro create <from>..<to>
```

Analyzes all files changed between the two refs and writes a retrospective to `.gitretro/retro-<from>-<to>/`.

Use `--force` to overwrite an existing retrospective for the same range:

```sh
gitretro create --force <from>..<to>
```

### Serve a retrospective

```sh
gitretro serve <from>..<to>
```

Opens the retrospective in your browser via `mdbook serve`.

### List all retrospectives

```sh
gitretro list
```

Displays all generated retrospectives and their included commits.

## How it works

1. `git diff --name-only` lists all changed files in the given range.
2. For each file, `git diff --patch` produces the raw unified diff.
3. The diff is sent to Gemini (`gemini-2.5-flash`) with a structured prompt that asks for a brief architectural summary, a per-change breakdown, and an impact statement.
4. Results are assembled into an mdbook project under `.gitretro/retro-<from>-<to>/`.

Rate-limit responses are parsed for retry delays. If all configured accounts are rate-limited beyond a threshold, the file is skipped and a warning is printed.

## License

MIT