# SEO Command Center — Forge Sprint 01

An AI-powered SEO audit tool built with Claude Code + Ollama.

## What it does
- Ingests any Screaming Frog CSV export
- Detects 17 SEO issues across 456+ URLs
- Generates automated title fixes
- Outputs report.json + report.html
- Live dashboard on localhost:7700

## How to run
```bash
pip install pandas flask
python run.py sample-export/internal_all.csv
```
Then open http://localhost:7700

## Architecture
- `ingest.py` — CSV parser, normalizes 12 columns
- `audit.py` — 17 SEO issue detectors (rulebook aligned)
- `fix.py` — title rewriter from URL slugs
- `dashboard.py` — Flask live dashboard
- `run.py` — master orchestrator

## Output
- `outputs/report.json` — machine readable report
- `outputs/report.html` — client ready report
- Dashboard at localhost:7700

## Stack
Claude Code + Ollama (gemma4:31b-cloud) + Python + Flask + Pandas