import pandas as pd
import sys

def fix(issues, df):
    # URL to row lookup for fast access
    url_map = {row['url']: row for _, row in df.iterrows()}
    
    fixes = []

    for issue in issues:
        url = issue['url']
        issue_type = issue['issue_type']
        row = url_map.get(url, {})

        if issue_type == 'missing_title':
            # Generate title from URL slug
            slug = url.rstrip('/').split('/')[-1]
            if not slug:
                slug = url.rstrip('/').split('/')[-2] if '/' in url.rstrip('/') else 'Home'
            new_title = slug.replace('-', ' ').replace('_', ' ').title()
            fixes.append({
                'url': url,
                'issue_type': issue_type,
                'original': '',
                'suggested_fix': new_title
            })

        elif issue_type == 'title_too_long':
            original = str(row.get('title', '')) if row else ''
            if len(original) > 60:
                truncated = original[:57] + '...'
            else:
                truncated = original
            fixes.append({
                'url': url,
                'issue_type': issue_type,
                'original': original,
                'suggested_fix': truncated
            })

        else:
            # No automated fix for other issues
            fixes.append({
                'url': url,
                'issue_type': issue_type,
                'original': issue.get('detail', ''),
                'suggested_fix': 'Manual review required'
            })

    return fixes

if __name__ == "__main__":
    # Quick test
    test_issues = [
        {'url': '/about-us/', 'issue_type': 'missing_title', 'severity': 'high', 'detail': ''},
        {'url': '/blog/my-long-title-that-goes-way-over-sixty-characters-limit/', 
         'issue_type': 'title_too_long', 'severity': 'medium', 'detail': ''},
    ]
    test_df = pd.DataFrame([
        {'url': '/about-us/', 'title': ''},
        {'url': '/blog/my-long-title-that-goes-way-over-sixty-characters-limit/', 
         'title': 'My Long Title That Goes Way Over Sixty Characters Limit'},
    ])
    results = fix(test_issues, test_df)
    for r in results:
        print(r)