# SEO Command Center — Forge Sprint 01

An AI-style SEO auditing platform built using Python, Flask, Pandas, Claude Code, and Ollama.

The system processes Screaming Frog exports, detects SEO issues using rule-based analysis, generates automated fix suggestions, and visualizes everything through a live dashboard.

---

# Features

## SEO Audit Engine

* Detects 17 SEO issues using rule-based analysis
* Supports duplicate title detection
* Detects missing metadata
* Identifies thin content pages
* Detects redirect and status code issues
* Detects oversized titles and meta descriptions

---

## Automated Fix Suggestions

* Generates SEO title suggestions automatically
* Uses URL slug parsing and formatting rules
* Produces human-readable recommendations

Examples:

* `/web-development`
  → `Professional Web Development Services`

* `/about-us`
  → `About Us | Company Name`

---

## Live Dashboard

* Flask-based live dashboard
* Dark theme UI
* Severity metrics
* Issue tables
* Suggested fix rendering
* Auto-refresh support

Accessible at:

```text
http://localhost:7700
```

---

# Architecture

## Pipeline Flow

```text
Screaming Frog Export
        ↓
internal_all.csv
        ↓
ingest.py
        ↓
audit.py
        ↓
fix.py
        ↓
report.json
        ↓
dashboard.py
        ↓
Flask Dashboard
```

---

# Core Modules

## ingest.py

Responsible for:

* Reading Screaming Frog CSV exports
* Column normalization
* Safe null handling
* Data preparation

---

## audit.py

Main rule-based SEO engine.

Detects:

* Missing titles
* Duplicate titles
* Thin content
* Redirects
* Broken links
* Metadata issues
* Status code issues

---

## fix.py

Generates automated fix suggestions using:

* URL parsing
* Slug formatting
* Template-based title generation

---

## dashboard.py

Flask-powered visualization layer.

Displays:

* Total URLs
* Total issues
* Severity breakdown
* Detailed issue table
* Suggested fixes

---

## run.py

Master pipeline orchestrator.

Executes:

1. CSV ingestion
2. SEO audit
3. Fix generation
4. Report creation
5. Dashboard launch

---

# Outputs

## outputs/report.json

Machine-readable structured SEO report.

Contains:

* issue summaries
* severity counts
* affected URLs
* recommendations

---

## outputs/report.html

Client-friendly visual report.

---

# Example Metrics

Processed:

* 456 URLs
* 201 detected SEO issues

Severity Breakdown:

* High: 12
* Medium: 84
* Low: 105

---

# Tech Stack

* Python
* Flask
* Pandas
* Claude Code
* Ollama
* HTML/CSS

---

# How to Run

## Install dependencies

```bash
pip install pandas flask
```

---

## Run the full pipeline

```bash
python run.py sample-export/internal_all.csv
```

---

## Open dashboard

```text
http://localhost:7700
```

---

# Development Notes

* Built using incremental commits
* Rulebook-aligned SEO detection
* Local-only stack (no paid APIs)
* Debugged severity aggregation issues
* Integrated automated fix suggestions into dashboard rendering

---

# Final Result

A complete local SEO auditing system capable of:

* processing Screaming Frog exports
* detecting SEO problems
* generating fix suggestions
* visualizing results through a live dashboard
