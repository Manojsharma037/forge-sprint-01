import pandas as pd

def fix(issues, df):
    """
    Provides suggested fixes for specific SEO issues.

    Args:
        issues (list): List of issue dicts {url, issue_type, severity, detail}
        df (pd.DataFrame): The ingested dataframe containing the page data.

    Returns:
        list: List of dicts {url, issue_type, original, suggested_fix}
    """
    fixes = []

    # Create a lookup for easy access to row data by URL
    # We assume URLs are unique in the dataframe
    url_map = df.set_index('url').to_dict('index')

    for issue in issues:
        url = issue['url']
        issue_type = issue['issue_type']

        # Get the row data for this URL
        row = url_map.get(url, {})

        if issue_type == 'missing_title':
            # Generate title from URL slug
            # 1. Remove trailing slash
            path = url.rstrip('/')
            # 2. Split by / and take last part
            slug = path.split('/')[-1] if '/' in path else path
            # 3. Replace hyphens with spaces and title case
            suggested = slug.replace('-', ' ').replace('_', ' ').title()

            # Fallback if slug is empty or just a number
            if not suggested or suggested.isdigit():
                suggested = "Home Page" if url == '/' else "Page Title"

            fixes.append({
                'url': url,
                'issue_type': issue_type,
                'original': '',
                'suggested_fix': suggested
            })

        elif issue_type == 'title_too_long':
            original_title = str(row.get('title', ''))
            if len(original_title) > 60:
                suggested = original_title[:60] + "..."
            else:
                suggested = original_title

            fixes.append({
                'url': url,
                'issue_type': issue_type,
                'original': original_title,
                'suggested_fix': suggested
            })

        else:
            # For issue types not explicitly handled, we provide a generic message
            fixes.append({
                'url': url,
                'issue_type': issue_type,
                'original': 'N/A',
                'suggested_fix': 'No automated fix available. Please review manually.'
            })

    return fixes

if __name__ == "__main__":
    # Test Data
    data = {
        'url': ['/blog/my-first-seo-post', '/about-us', '/services/web-design-and-development-for-small-businesses-in-the-city'],
        'title': ['', 'About Us', 'Web Design and Development for Small Businesses in the City - Best Agency 2024'],
        'status_code': [200, 200, 200],
        'indexable': ['Indexable', 'Indexable', 'Indexable'],
    }
    df_test = pd.DataFrame(data)

    # Mock issues from audit.py
    mock_issues = [
        {'url': '/blog/my-first-seo-post', 'issue_type': 'missing_title', 'severity': 'High', 'detail': '...'},
        {'url': '/services/web-design-and-development-for-small-businesses-in-the-city', 'issue_type': 'title_too_long', 'severity': 'Medium', 'detail': '...'},
        {'url': '/about-us', 'issue_type': 'broken_link', 'severity': 'High', 'detail': '...'}
    ]

    results = fix(mock_issues, df_test)
    print(f"Generated {len(results)} fixes:\n")
    for res in results:
        print(f"URL: {res['url']}")
        print(f"Issue: {res['issue_type']}")
        print(f"Original: {res['original']}")
        print(f"Fix: {res['suggested_fix']}")
        print("-" * 30)
