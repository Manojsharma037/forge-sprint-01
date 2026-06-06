import pandas as pd

def fix(issues, df):
    url_map = df.set_index('url').to_dict('index')
    fixes = []

    for issue in issues:
        url = issue['url']
        issue_type = issue['issue_type']
        row = url_map.get(url, {})
        original = str(row.get('title', '')) if row else ''

        if issue_type == 'missing_title':
            slug = url.rstrip('/').split('/')[-1] or 'home'
            new_title = slug.replace('-', ' ').replace('_', ' ').title()
            fixes.append({'url': url, 'issue_type': issue_type,
                'original': '', 'suggested_fix': new_title})

        elif issue_type == 'title_too_long':
            truncated = original[:57] + '...' if len(original) > 60 else original
            fixes.append({'url': url, 'issue_type': issue_type,
                'original': original, 'suggested_fix': truncated})

        else:
            fixes.append({'url': url, 'issue_type': issue_type,
                'original': original,
                'suggested_fix': 'Manual review required'})

    return fixes