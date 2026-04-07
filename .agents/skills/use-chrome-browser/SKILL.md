---
name: use-chrome-browser
description: Use Rodney (uvx rodney) to drive Chrome for deterministic browser interactions, assertions, screenshots, and accessibility checks from the CLI.
compatibility: Requires uvx, Rodney, and local Chrome/Chromium availability
metadata:
  author: longtail-experiment
  source: simonw/rodney README and local --help output
---

Run `uvx rodney --help` before running anything else.

# Use Chrome Browser Skill

## User Input

```text
$ARGUMENTS
```

You MUST consider the user input before proceeding (if not empty).

## Purpose

Use Rodney as a persistent Chrome automation CLI so agents can perform reliable browser interactions across multiple commands without re-creating browser state each step.

## When to Use

Use this skill when a task requires real browser behavior, such as:

- opening pages and navigating flows
- interacting with form controls
- waiting for async rendering/network activity
- validating UI conditions in scripts/CI with exit codes
- capturing screenshots or PDFs
- running accessibility checks through the Chrome accessibility tree

## Core Operating Model

1. Rodney commands are short-lived, but they connect to one long-running Chrome session.
2. Start a session first, then execute interaction commands, then stop the session.
3. Prefer deterministic waits (`wait`, `waitload`, `waitstable`, `waitidle`) over blind sleeps.
4. Treat Rodney exit codes as contract signals:
   - `0`: success
   - `1`: check/assert condition failed
   - `2`: command/runtime error
5. Always clean up with `uvx rodney stop` when done.
6. For UI visual validation, screenshots are required evidence and must be reviewed directly.

## Required Workflow

1. Run `uvx rodney --help` first.
2. Start or connect a browser session:
   - `uvx rodney start` for default headless mode
   - `uvx rodney start --show` when visible debugging is needed
   - `uvx rodney connect <host:port>` when reusing external Chrome
3. Navigate and synchronize:
   - `uvx rodney open <url>`
   - wait using `waitload`, `waitstable`, `waitidle`, or selector-based `wait`
4. Perform actions and assertions:
   - interactions: `click`, `input`, `select`, `submit`, `hover`, `focus`, `file`
   - checks: `exists`, `visible`, `assert`, `count`, `ax-find`
5. Capture artifacts when useful:
    - `screenshot`, `screenshot-el`, `pdf`, `html`
6. For visual component validation, screenshots are not optional:
   - capture screenshots for every impacted visual state (at minimum: initial state + changed state),
   - manually inspect screenshot output for layering/background/contrast/spacing/overflow defects,
   - do not sign off visual correctness from computed styles alone,
   - when computed styles and screenshot appearance disagree, treat the screenshot as source of truth and report/fix the regression.
7. Stop session:
    - `uvx rodney stop`

## Session Scope Rules

- Rodney auto-detects local session state (`./.rodney/state.json`) before global state.
- Use `--local` for directory-scoped, isolated sessions when task isolation matters.
- Use `--global` to force shared session usage.
- Add `.rodney/` to `.gitignore` if local sessions are used in-repo.

## Reliable Automation Patterns

### Pattern A: Basic page check

```bash
uvx rodney --help
uvx rodney start
uvx rodney open "https://example.com"
uvx rodney waitstable
uvx rodney assert 'document.title' 'Example Domain' -m "Unexpected title"
uvx rodney visible "h1"
uvx rodney screenshot example-home.png
uvx rodney stop
```

### Pattern B: Form flow

```bash
uvx rodney --help
uvx rodney start
uvx rodney open "https://example.com/login"
uvx rodney wait "form#login"
uvx rodney input "#email" "user@example.com"
uvx rodney input "#password" "correct-horse-battery-staple"
uvx rodney click "button[type=submit]"
uvx rodney waitidle
uvx rodney assert 'document.querySelector(".dashboard") !== null' -m "Login did not reach dashboard"
uvx rodney stop
```

### Pattern C: Accessibility guardrail

```bash
uvx rodney --help
uvx rodney start
uvx rodney open "https://example.com"
uvx rodney waitstable
uvx rodney ax-find --role button --json
uvx rodney ax-node "#submit-btn" --json
uvx rodney stop
```

## Command Families (Quick Reference)

- Lifecycle: `start`, `connect`, `status`, `stop`
- Navigation: `open`, `back`, `forward`, `reload`, `clear-cache`
- Inspection: `url`, `title`, `text`, `html`, `attr`, `js`
- Interaction: `click`, `input`, `clear`, `file`, `download`, `select`, `submit`, `hover`, `focus`
- Waiting: `wait`, `waitload`, `waitstable`, `waitidle`, `sleep`
- Artifacts: `screenshot`, `screenshot-el`, `pdf`
- Tabs: `pages`, `page`, `newpage`, `closepage`
- Checks: `exists`, `visible`, `count`, `assert`
- Accessibility: `ax-tree`, `ax-find`, `ax-node`

## Troubleshooting

1. If commands fail with session errors, run `uvx rodney status`; if needed, restart with `uvx rodney stop` then `uvx rodney start`.
2. If selectors are flaky, wait for stable state (`waitstable` or selector-specific `wait`) before interaction.
3. If HTTPS cert issues block automation in test environments, use `uvx rodney start --insecure`.
4. If check commands fail, treat exit code `1` as a product assertion failure, not a Rodney runtime crash.

## Completion Checklist

Before ending browser work:

1. Required interactions and assertions were executed.
2. For visual/UI validation, screenshots of all impacted states were captured and visually reviewed.
3. Browser session was closed with `uvx rodney stop`.
4. Report includes commands run and key observed outcomes.
