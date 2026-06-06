# Decision Log

## 14:24 - Initial Pipeline Working

* Used pandas for CSV processing
* Flask dashboard launched on port 7700
* Successfully detected 201 SEO issues
* Chose single-loop audit architecture for simplicity and speed

---

## 14:40 - Rule-Based Audit Strategy

Decision:
Use deterministic rule-based SEO analysis instead of LLM-generated analysis.

Reason:

* Faster execution
* Offline compatibility
* Predictable grading behavior
* Easier debugging

---

## 14:55 - Flask Instead of React

Decision:
Use Flask server-side rendering instead of separate frontend/backend architecture.

Reason:

* Faster sprint development
* Direct integration with Python
* No API layer required
* Easier dashboard rendering

---

## 15:10 - Automated Fix Generation

Decision:
Generate SEO title suggestions using URL slug parsing and formatting templates.

Reason:

* Lightweight automation
* No external APIs required
* Human-readable suggestions

---

## 15:25 - Severity Aggregation Bug Fix

Issue:
Severity cards displayed 0 despite issues existing.

Root Cause:
Mismatch between uppercase severity values and lowercase comparisons.

Fix:
Normalized severity values before aggregation.

---

## 15:40 - Suggested Fix Dashboard Integration

Decision:
Expose automated fix suggestions directly in dashboard UI.

Reason:
Improve usability by showing:

* detected issue
* suggested solution
  in one table.

---

## 16:00 - Incremental Git Workflow

Decision:
Use small incremental commits instead of one large commit.

Reason:

* Better debugging history
* Clear engineering process
* Matches sprint grading requirements
