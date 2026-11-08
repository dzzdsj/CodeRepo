# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo context

This directory (`project/dev-assistant`) is an empty scaffold inside the `CodeRepo` monorepo. The actual git root is the parent directory `/Users/dzzdsj/git/dzzdsj-git/github/CodeRepo`, not this folder — so `git` commands run here operate on the whole monorepo, which also contains unrelated projects under `java/`, `python/`, `vue/`, `shell/`, `script/`, `office/`, `C/`, and other `project/*` subprojects.

## Current state

- `backend/` and `frontend/` exist but are empty (no code, no config, no package manifests).
- There are no build, lint, test, or run commands yet, and no README or rules files.
- Nothing is implemented; treat this as a greenfield project.

## Nearest reference in this repo

`project/aidevops` is the sibling project that most closely matches the intended shape of this kind of app in this monorepo: a FastAPI backend (`project/aidevops/backend`, with `app/`, `alembic/`, `tests/`, `pytest.ini`, `requirements*.txt`) and a Vue 3 + Vite frontend (`project/aidevops/frontend`). It is a separate, unrelated project — use it only as a structural/pattern reference if a similar stack is adopted here, not as a source of truth for this directory.

Until real code lands, this file should be expanded with the actual build/run/test commands and architecture once `backend/` and `frontend/` are populated.
