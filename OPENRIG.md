# OpenRig 0.6.0 on Garrett.ai

OpenRig is the seat layer. It is not the organism.
Garrett.ai remains the one process (`ai-orchestrator`).
OpenRig boots Claude Code / Codex seats against this repo.

Upstream: https://github.com/mvschwarz/openrig
Package: `@openrig/cli@0.6.0`
Release commit: `57380a250e797c182a336e97afe2e0edb841ba9c`

## Requirements

- Node.js **22 or 24** (not 20, not 26)
- tmux
- macOS or Linux (native Windows unsupported; Apple silicon → Node 22)
- At least one harness logged in (Codex for `first-project`)

`rig setup` writes hooks and trust files under `~/.openrig`, `~/.tmux.conf`, Codex/Claude configs. Dry-run first.

## Boot against this runtime

```bash
nvm install 22   # if you are still on 20
npm install -g @openrig/cli@0.6.0
rig --version    # expect 0.6.0

cd ai-orchestrator
rig setup --dry-run
rig setup

rig up first-project --cwd . --plan
rig up first-project --cwd .
rig ps --nodes --rig first-project
rig tui --shared
```

Owner address: `dev-owner@first-project`
Checker address: `dev-checker@first-project` (starter naming; inspect `rig ps`)

Send one bounded change only:

```bash
rig send dev-owner@first-project 'Implement one bounded change in backend/packages.py: add OpenRig as an external seat package in summary() output. Do not invent AGI. Checker verifies the exact diff.'
```

## What stays off

- Slack manifest and Jev/Rig Stream classifier are experimental and off by default. Not routing.
- Do not run `rig up` on the Apex `:8000` host until Node 22 + tmux exist there.
- OpenRig does not replace `/v1/run`, Stripe, or HubSpot.
