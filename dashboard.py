from flask import Flask, jsonify, render_template_string
import json
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SEO Command Center</title>
    <meta http-equiv="refresh" content="5">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 20px; }
        h1 { color: #00ff88; margin-bottom: 20px; font-size: 24px; }
        .stats { display: flex; gap: 20px; margin-bottom: 30px; }
        .card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; min-width: 150px; text-align: center; }
        .card h2 { font-size: 36px; font-weight: bold; }
        .card p { color: #888; font-size: 14px; margin-top: 5px; }
        .high { color: #ff4444; }
        .medium { color: #ffaa00; }
        .low { color: #44aaff; }
        .total { color: #00ff88; }
        table { width: 100%; border-collapse: collapse; background: #1a1a1a; border-radius: 8px; overflow: hidden; }
        th { background: #252525; padding: 12px; text-align: left; color: #888; font-size: 13px; }
        td { padding: 10px 12px; border-bottom: 1px solid #252525; font-size: 13px; }
        tr:hover { background: #222; }
        .badge { padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .badge-high { background: #ff444433; color: #ff4444; }
        .badge-medium { background: #ffaa0033; color: #ffaa00; }
        .badge-low { background: #44aaff33; color: #44aaff; }
        .url { color: #888; font-size: 11px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    </style>
</head>
<body>
    <h1>🔍 SEO Command Center</h1>

    {% if data %}
    <div class="stats">
        <div class="card">
            <h2 class="total">{{ data.summary.total_urls }}</h2>
            <p>Total URLs</p>
        </div>
        <div class="card">
            <h2 class="total">{{ data.summary.total_issues }}</h2>
            <p>Total Issues</p>
        </div>
        <div class="card">
            <h2 class="high">{{ data.summary.by_severity.get('high', 0) }}</h2>
            <p>High</p>
        </div>
        <div class="card">
            <h2 class="medium">{{ data.summary.by_severity.get('medium', 0) }}</h2>
            <p>Medium</p>
        </div>
        <div class="card">
            <h2 class="low">{{ data.summary.by_severity.get('low', 0) }}</h2>
            <p>Low</p>
        </div>
    </div>

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
            {% for issue in data.issues %}
            <tr>
                <td class="url" title="{{ issue.url }}">{{ issue.url }}</td>
                <td>{{ issue.issue_type }}</td>
                <td><span class="badge badge-{{ issue.severity }}">{{ issue.severity.upper() }}</span></td>
                <td>{{ issue.detail }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p style="color:#888; margin-top: 40px;">⏳ Waiting for audit to run... Run python run.py to start.</p>
    {% endif %}
</body>
</html>
"""

def load_report():
    path = os.path.join(os.path.dirname(__file__), 'outputs', 'report.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

@app.route('/')
def index():
    data = load_report()
    return render_template_string(HTML, data=data)

@app.route('/api/report')
def api_report():
    data = load_report()
    if data:
        return jsonify(data)
    return jsonify({'error': 'No report yet'}), 404

if __name__ == "__main__":
    print("Dashboard running at http://localhost:7700")
    app.run(host='0.0.0.0', port=7700, debug=False)