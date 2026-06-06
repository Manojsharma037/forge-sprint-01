import json
import os
import pandas as pd
from ingest import ingest
from audit import audit
from fix import fix

# The target report files
REPORT_JSON = 'outputs/report.json'
REPORT_HTML = 'outputs/report.html'

def generate_html_report(issues, fixes, total_pages, filename):
    """Generates a standalone static HTML report."""

    high = len([i for i in issues if i['severity'] == 'High'])
    med = len([i for i in issues if i['severity'] == 'Medium'])
    low = len([i for i in issues if i['severity'] == 'Low'])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>SEO Audit Report - {filename}</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #f8f9fa; color: #333; }}
            .header {{ background: #2c3e50; color: white; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }}
            .container {{ padding: 20px 40px; max-width: 1200px; margin: 0 auto; }}
            .section {{ margin-bottom: 50px; }}
            .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-box {{ padding: 20px; border-radius: 12px; text-align: center; color: white; }}
            .bg-blue {{ background: #3498db; }} .bg-red {{ background: #e74c3c; }} .bg-orange {{ background: #f39c12; }} .bg-green {{ background: #2ecc71; }}
            .value {{ font-size: 2.5rem; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ text-align: left; padding: 12px 15px; border-bottom: 1px solid #eee; }}
            th {{ background-color: #fcfcfc; color: #7f8c8d; font-size: 0.85rem; }}
            .severity-High {{ color: #e74c3c; font-weight: bold; }}
            .severity-Medium {{ color: #f39c12; font-weight: bold; }}
            .severity-Low {{ color: #2ecc71; font-weight: bold; }}
            .fix-suggested {{ font-weight: bold; color: #27ae60; }}
            a {{ color: #3498db; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>SEO Audit Report</h1>
            <div>File: <strong>{filename}</strong></div>
        </div>
        <div class="container">
            <div class="section">
                <h2>Summary Overview</h2>
                <div class="stat-grid">
                    <div class="stat-box bg-blue"><h3>Total Pages</h3><div class="value">{total_pages}</div></div>
                    <div class="stat-box bg-red"><h3>High Severity</h3><div class="value">{high}</div></div>
                    <div class="stat-box bg-orange"><h3>Medium Severity</h3><div class="value">{med}</div></div>
                    <div class="stat-box bg-green"><h3>Low Severity</h3><div class="value">{low}</div></div>
                </div>
            </div>

            <div class="section">
                <h2>Detected Issues</h2>
                <div class="card">
                    <table>
                        <thead><tr><th>URL</th><th>Issue Type</th><th>Severity</th><th>Detail</th></tr></thead>
                        <tbody>
                            {''.join([f'<tr><td><a href="{i["url"]}" target="_blank">{i["url"]}</a></td><td>{i["issue_type"]}</td><td class="severity-{i["severity"]}">{i["severity"]}</td><td>{i["detail"]}</td></tr>' for i in issues])}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="section">
                <h2>Suggested Fixes</h2>
                <div class="card">
                    <table>
                        <thead><tr><th>URL</th><th>Issue</th><th>Original</th><th>Suggested Fix</th></tr></thead>
                        <tbody>
                            {''.join([f'<tr><td><a href="{f["url"]}" target="_blank">{f["url"]}</a></td><td>{f["issue_type"]}</td><td>{f["original"]}</td><td class="fix-suggested">{f["suggested_fix"]}</td></tr>' for f in fixes])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def main():
    input_csv = 'internal_all.csv'

    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found. Please place the CSV in the root directory.")
        return

    print(f"--- Starting SEO Audit Pipeline for {input_csv} ---")

    # 1. Ingest
    df = ingest(input_csv)
    print(f"Ingested {len(df)} pages.")

    # 2. Audit
    issues = audit(df)
    print(f"Detected {len(issues)} issues.")

    # 3. Fix
    fixes = fix(issues, df)
    print(f"Generated {len(fixes)} fix suggestions.")

    # 4. Save JSON report
    report_data = {
        'summary': {
            'total_pages': len(df),
            'total_issues': len(issues),
            'high': len([i for i in issues if i['severity'] == 'High']),
            'medium': len([i for i in issues if i['severity'] == 'Medium']),
            'low': len([i for i in issues if i['severity'] == 'Low']),
        },
        'issues': issues,
        'fixes': fixes
    }

    os.makedirs('outputs', exist_ok=True)
    with open(REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=4)
    print(f"JSON report saved to {REPORT_JSON}")

    # 5. Save HTML report
    html_content = generate_html_report(issues, fixes, len(df), input_csv)
    with open(REPORT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML report saved to {REPORT_HTML}")

    print("\n--- Audit Complete ---")
    print(f"URLs with issues: {len(set(i['url'] for i in issues))}")

if __name__ == "__main__":
    main()
