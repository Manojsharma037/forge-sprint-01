from flask import Flask, render_template_string, request
import pandas as pd
from ingest import ingest
from audit import audit
from fix import fix

app = Flask(__name__)

# Global cache to avoid re-running audit on every refresh
cache = {
    'df': None,
    'issues': None,
    'fixes': None,
    'filename': None
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SEO Audit Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f8f9fa; color: #333; }
        .header { background: #2c3e50; color: white; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
        .container { padding: 20px 40px; max-width: 1200px; margin: 0 auto; }

        nav { position: sticky; top: 0; background: #fff; padding: 15px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); z-index: 1000; text-align: center; }
        nav a { margin: 0 15px; text-decoration: none; color: #2c3e50; font-weight: 600; padding: 8px 16px; border-radius: 4px; transition: background 0.3s; }
        nav a:hover { background: #e9ecef; }

        .section { margin-bottom: 50px; scroll-margin-top: 80px; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h1, h2 { color: #2c3e50; }

        .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-box { padding: 20px; border-radius: 12px; text-align: center; color: white; transition: transform 0.2s; }
        .stat-box:hover { transform: translateY(-5px); }
        .stat-box h3 { margin: 0; font-size: 1rem; opacity: 0.9; }
        .stat-box .value { font-size: 2.5rem; font-weight: bold; margin: 10px 0; }

        .bg-blue { background: #3498db; }
        .bg-red { background: #e74c3c; }
        .bg-orange { background: #f39c12; }
        .bg-green { background: #2ecc71; }

        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
        th, td { text-align: left; padding: 12px 15px; border-bottom: 1px solid #eee; }
        th { background-color: #fcfcfc; color: #7f8c8d; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; }
        tr:hover { background-color: #fdfdfd; }

        .severity-High { color: #e74c3c; font-weight: bold; }
        .severity-Medium { color: #f39c12; font-weight: bold; }
        .severity-Low { color: #2ecc71; font-weight: bold; }

        code { background: #f1f1f1; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.9em; }
        .fix-suggested { font-weight: bold; color: #27ae60; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SEO Audit Dashboard</h1>
        <div>File: <strong>{{ filename }}</strong></div>
    </div>

    <nav>
        <a href="#overview">Overview</a>
        <a href="#issues">Detected Issues</a>
        <a href="#fixes">Suggested Fixes</a>
    </nav>

    <div class="container">
        <!-- SECTION: OVERVIEW -->
        <div id="overview" class="section">
            <h2>Summary Overview</h2>
            <div class="stat-grid">
                <div class="stat-box bg-blue">
                    <h3>Total Pages</h3>
                    <div class="value">{{ total_pages }}</div>
                </div>
                <div class="stat-box bg-red">
                    <h3>High Severity</h3>
                    <div class="value">{{ high_count }}</div>
                </div>
                <div class="stat-box bg-orange">
                    <h3>Medium Severity</h3>
                    <div class="value">{{ med_count }}</div>
                </div>
                <div class="stat-box bg-green">
                    <h3>Low Severity</h3>
                    <div class="value">{{ low_count }}</div>
                </div>
            </div>
            <div class="card">
                <p><strong>Audit Summary:</strong> Found <u>{{ total_issues }}</u> issues across <u>{{ total_pages }}</u> pages.
                <u>{{ fixes_count }}</u> automated fixes have been generated for high-impact items.</p>
            </div>
        </div>

        <!-- SECTION: ISSUES -->
        <div id="issues" class="section">
            <h2>Detected Issues</h2>
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>URL</th>
                            <th>Issue Type</th>
                            <th>Severity</th>
                            <th>Detail</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for issue in issues %}
                        <tr>
                            <td><a href="{{ issue.url }}" target="_blank">{{ issue.url }}</a></td>
                            <td><code>{{ issue.issue_type }}</code></td>
                            <td class="severity-{{ issue.severity }}">{{ issue.severity }}</td>
                            <td>{{ issue.detail }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- SECTION: FIXES -->
        <div id="fixes" class="section">
            <h2>Automated Fix Suggestions</h2>
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>URL</th>
                            <th>Issue</th>
                            <th>Original Content</th>
                            <th>Suggested Fix</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for f in fixes %}
                        <tr>
                            <td><a href="{{ f.url }}" target="_blank">{{ f.url }}</a></td>
                            <td><code>{{ f.issue_type }}</code></td>
                            <td>{{ f.original }}</td>
                            <td class="fix-suggested">{{ f.suggested_fix }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

def get_data():
    filename = request.args.get('file', 'internal_all.csv')
    if cache['filename'] == filename and cache['df'] is not None:
        return cache['df'], cache['issues'], cache['fixes'], cache['filename']

    try:
        df = ingest(filename)
        issues = audit(df)
        fixes = fix(issues, df)
        cache.update({'df': df, 'issues': issues, 'fixes': fixes, 'filename': filename})
        return df, issues, fixes, filename
    except Exception as e:
        print(f"Error processing file: {e}")
        return None, None, None, filename

@app.route('/')
def index():
    df, issues, fixes, filename = get_data()
    if df is None:
        return f"<h1>Error loading data</h1><p>Could not read <b>{filename}</b>. Please ensure the file exists.</p>", 500

    high = len([i for i in issues if i['severity'] == 'High'])
    med = len([i for i in issues if i['severity'] == 'Medium'])
    low = len([i for i in issues if i['severity'] == 'Low'])

    return render_template_string(
        HTML_TEMPLATE,
        total_pages=len(df),
        total_issues=len(issues),
        high_count=high,
        med_count=med,
        low_count=low,
        fixes_count=len(fixes),
        issues=issues,
        fixes=fixes,
        filename=filename
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7700, debug=True)
