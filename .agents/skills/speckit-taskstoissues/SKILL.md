---
name: speckit-taskstoissues
description:
  Convert task phases from tasks.md into GitHub issues. Use after task breakdown
  to track work items in GitHub project management.
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: github-spec-kit
  source: templates/commands/taskstoissues.md
---

# Speckit Taskstoissues Skill

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").
2. From the executed script, extract the path to **tasks**.
3. Get the Git remote by running:

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> ONLY PROCEED TO NEXT STEPS IF THE REMOTE IS A GITHUB URL

4. The tasks.md file will contain a list of tasks broken up into numbered phases. For each PHASE, create a GitHub issue with the phase name as the title and the list of tasks as the body. Use the GitHub MCP server to create the issues in the repository that is representative of the Git remote.

> [!CAUTION]
> UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES THAT DO NOT MATCH THE REMOTE URL

> [!CAUTION]
> ONLY CREATE ISSUES FOR PHASES, NOT FOR INDIVIDUAL TASKS. THE PHASE NAMES SHOULD BE USED AS ISSUE TITLES AND THE TASKS SHOULD BE INCLUDED IN THE ISSUE BODIES.
