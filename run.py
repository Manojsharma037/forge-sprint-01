import sys, json, os, threading
from ingest import ingest
from audit import audit
from fix import fix
from dashboard import app

def save_report(df, issues, fixes):
    os.makedirs('outputs', exist_ok=True)
    for i in issues:
        i['severity'] = i['severity'].lower()
    fix_map = {(f['url'], f['issue_type']): f.get('suggested_fix', '') for f in fixes}
    for i in issues:
        i['suggested_fix'] = fix_map.get((i['url'], i['issue_type']), 'Manual review required')
    by_severity = {}
    for i in issues:
        s = i['severity']
        by_severity[s] = by_severity.get(s, 0) + 1
    report = {
        'summary': {
            'total_urls': len(df),
            'total_issues': len(issues),
            'by_severity': by_severity,
            'high': by_severity.get('high', 0),
            'medium': by_severity.get('medium', 0),
            'low': by_severity.get('low', 0),
        },
        'issues': issues,
        'fixes': fixes
    }
    with open('outputs/report.json', 'w') as f:
        json.dump(report, f, indent=2)
    html = f"""<!DOCTYPE html><html><head><title>SEO Report</title>
    <style>body{{font-family:Arial;padding:20px}}table{{border-collapse:collapse;width:100%}}
    th,td{{border:1px solid #ddd;padding:8px}}th{{background:#f2f2f2}}
    .high{{color:red}}.medium{{color:orange}}.low{{color:blue}}</style></head>
    <body><h1>SEO Audit Report</h1>
    <p>Total URLs: {len(df)} | Total Issues: {len(issues)}</p>
    <table><tr><th>URL</th><th>Issue</th><th>Severity</th><th>Detail</th><th>Suggested Fix</th></tr>
    {''.join(f"<tr><td>{i['url']}</td><td>{i['issue_type']}</td><td class='{i['severity']}'>{i['severity'].upper()}</td><td>{i['detail']}</td><td>{i.get('suggested_fix','—')}</td></tr>" for i in issues)}
    </table></body></html>"""
    with open('outputs/report.html', 'w') as f:
        f.write(html)
    print(f"Done! {len(issues)} issues found. Report saved.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <csv_path>")
        sys.exit(1)
    csv_path = sys.argv[1]
    print(f"Reading {csv_path}...")
    df = ingest(csv_path)
    print(f"Auditing {len(df)} URLs...")
    issues = audit(df)
    fixes = fix(issues, df)
    save_report(df, issues, fixes)
    print("Starting dashboard at http://localhost:7700")
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=7700), daemon=True).start()
    input("Press Enter to stop...")