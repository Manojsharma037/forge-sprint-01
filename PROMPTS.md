# Key Prompts Used

## 1. Initial Project Scaffold

Created the initial project structure with:

* ingest.py
* audit.py
* fix.py
* dashboard.py
* run.py
* outputs/
* documentation files

Goal:
Set up a modular SEO audit pipeline.

---

## 2. CSV Ingestion Logic

Prompted for flexible CSV ingestion using pandas with:

* fallback column matching
* safe null handling
* support for Screaming Frog internal_all.csv

Reason:
Different exports may contain slightly different column names.

---

## 3. SEO Audit Engine

Prompted for rule-based SEO detectors aligned with rulebook.md.

Implemented checks for:

* duplicate titles
* missing titles
* title length
* meta description length
* thin content
* redirect detection
* broken links
* server errors

Decision:
Use a single-loop architecture for performance.

---

## 4. Automated Fix Suggestions

Prompted for automated title suggestion generation using URL slug parsing.

Examples:

* /web-development
  → Professional Web Development Services

* /about-us
  → About Us | Company Name

Goal:
Generate human-readable SEO title suggestions automatically.

---

## 5. Flask Dashboard UI

Prompted for a dark-themed Flask dashboard with:

* severity cards
* issue tables
* auto-refresh
* responsive layout

Goal:
Visualize audit results in real time.

---

## 6. Debugging Severity Aggregation

Identified a bug where HIGH/MEDIUM/LOW counts showed 0.

Root cause:
Case mismatch between stored severity values and comparison logic.

Fix:
Normalized severity values using .lower() before aggregation.

---

## 7. Suggested Fix Integration

Extended dashboard rendering to include:

* Suggested Fix column
* backend/frontend integration
* fix.py output rendering

Goal:
Show both detected problems and automated solutions.

---

## 8. Final Pipeline Orchestration

Prompted for a master run.py orchestrator to:

* execute ingestion
* run audits
* generate fixes
* write reports
* launch dashboard

Goal:
Allow complete execution using one command.
