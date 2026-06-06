import pandas as pd
import sys

def audit(df):
    """
    Performs an SEO audit based on the Rulebook.
    Returns a list of dicts: {url, issue_type, severity, detail}
    """
    issues = []

    # -------------------------------------------------------------------------
    # PRE-FILTERS & HELPER DATASETS
    # -------------------------------------------------------------------------

    # Rule: Only consider rows where `Content Type` contains `text/html`
    # We assume 'content_type' is available in the df.
    # If not, we proceed with all rows (fallback).
    if 'content_type' in df.columns:
        df_html = df[df['content_type'].str.contains('text/html', na=False, case=False)].copy()
    else:
        df_html = df.copy()

    # Rule: A page is "indexable" when `Indexability` = `Indexable`
    # We use the standardized column name 'indexable' from ingest.py
    def is_indexable(row):
        return str(row.get('indexable', '')).strip() == 'Indexable'

    # Rule: For "duplicate" checks, only compare Indexable 200 pages.
    # Let's define the subset of indexable 200 pages.
    indexable_200_mask = (
        (df_html['status_code'] == 200) &
        (df_html.apply(is_indexable, axis=1))
    )
    df_idx200 = df_html[indexable_200_mask]

    # -------------------------------------------------------------------------
    # DETECTORS
    # -------------------------------------------------------------------------

    # 1. missing_title: Title 1 empty, indexable 200 page
    # Severity: High
    for _, row in df_idx200.iterrows():
        if not row['title'] or str(row['title']).strip() == '':
            issues.append({
                'url': row['url'],
                'issue_type': 'missing_title',
                'severity': 'High',
                'detail': 'Page title is missing on an indexable 200 page.'
            })

    # 2. duplicate_title: same Title 1 on 2+ indexable URLs (restricted to 200s per pre-filter)
    # Severity: High
    title_counts = df_idx200[df_idx200['title'].str.strip() != '']['title'].value_counts()
    dupe_titles = title_counts[title_counts >= 2].index
    for _, row in df_idx200.iterrows():
        if row['title'] in dupe_titles:
            issues.append({
                'url': row['url'],
                'issue_type': 'duplicate_title',
                'severity': 'High',
                'detail': f"Duplicate title found: {row['title']}"
            })

    # 3. title_too_long: Title 1 Pixel Width > 561 OR Title 1 Length > 60
    # Severity: Medium
    for _, row in df_html.iterrows():
        length = len(str(row['title'])) if row['title'] else 0
        pixel_width = row.get('title_pixel_width', 0)
        if pixel_width > 561 or length > 60:
            issues.append({
                'url': row['url'],
                'issue_type': 'title_too_long',
                'severity': 'Medium',
                'detail': f"Title too long (Length: {length}, Pixel Width: {pixel_width})"
            })

    # 4. title_too_short: Title 1 Length < 30 (and not empty)
    # Severity: Low
    for _, row in df_html.iterrows():
        title_str = str(row['title']) if row['title'] else ''
        length = len(title_str)
        if 0 < length < 30:
            issues.append({
                'url': row['url'],
                'issue_type': 'title_too_short',
                'severity': 'Low',
                'detail': f"Title too short (Length: {length})"
            })

    # 5. missing_meta_description: Meta Description 1 empty, indexable 200 page
    # Severity: Medium
    for _, row in df_idx200.iterrows():
        if not row['meta_desc'] or str(row['meta_desc']).strip() == '':
            issues.append({
                'url': row['url'],
                'issue_type': 'missing_meta_description',
                'severity': 'Medium',
                'detail': 'Meta description is missing on an indexable 200 page.'
            })

    # 6. duplicate_meta_description: same Meta Description 1 on 2+ indexable URLs
    # Severity: Medium
    meta_counts = df_idx200[df_idx200['meta_desc'].str.strip() != '']['meta_desc'].value_counts()
    dupe_metas = meta_counts[meta_counts >= 2].index
    for _, row in df_idx200.iterrows():
        if row['meta_desc'] in dupe_metas:
            issues.append({
                'url': row['url'],
                'issue_type': 'duplicate_meta_description',
                'severity': 'Medium',
                'detail': f"Duplicate meta description found: {row['meta_desc']}"
            })

    # 7. meta_description_too_long: Meta Description 1 Length > 155
    # Severity: Low
    for _, row in df_html.iterrows():
        length = len(str(row['meta_desc'])) if row['meta_desc'] else 0
        if length > 155:
            issues.append({
                'url': row['url'],
                'issue_type': 'meta_description_too_long',
                'severity': 'Low',
                'detail': f"Meta description too long (Length: {length})"
            })

    # 8. missing_h1: H1-1 empty on a 200 page
    # Severity: Medium
    for _, row in df_html[df_html['status_code'] == 200].iterrows():
        if not row['h1'] or str(row['h1']).strip() == '':
            issues.append({
                'url': row['url'],
                'issue_type': 'missing_h1',
                'severity': 'Medium',
                'detail': 'H1 is missing on a 200 page.'
            })

    # 9. duplicate_h1: same H1-1 on 2+ indexable URLs
    # Severity: Low
    h1_counts = df_idx200[df_idx200['h1'].str.strip() != '']['h1'].value_counts()
    dupe_h1s = h1_counts[h1_counts >= 2].index
    for _, row in df_idx200.iterrows():
        if row['h1'] in dupe_h1s:
            issues.append({
                'url': row['url'],
                'issue_type': 'duplicate_h1',
                'severity': 'Low',
                'detail': f"Duplicate H1 found: {row['h1']}"
            })

    # 10. broken_link: Status Code in 400–499
    # Severity: High
    for _, row in df_html.iterrows():
        if 400 <= row['status_code'] < 500:
            issues.append({
                'url': row['url'],
                'issue_type': 'broken_link',
                'severity': 'High',
                'detail': f"Broken link with status code {row['status_code']}"
            })

    # 11. server_error: Status Code in 500–599
    # Severity: High
    for _, row in df_html.iterrows():
        if 500 <= row['status_code'] < 600:
            issues.append({
                'url': row['url'],
                'issue_type': 'server_error',
                'severity': 'High',
                'detail': f"Server error with status code {row['status_code']}"
            })

    # 12. redirect: Status Code in 300–399
    # Severity: Medium
    for _, row in df_html.iterrows():
        if 300 <= row['status_code'] < 400:
            issues.append({
                'url': row['url'],
                'issue_type': 'redirect',
                'severity': 'Medium',
                'detail': f"Redirect with status code {row['status_code']}"
            })

    # 13. redirect_chain: a redirect whose Redirect URL is itself a redirecting URL
    # Severity: High
    redirect_map = {}
    for _, row in df_html[ (df_html['status_code'] >= 300) & (df_html['status_code'] < 400) ].iterrows():
        redirect_map[row['url']] = row.get('redirect_url')

    for url, target in redirect_map.items():
        if target and target in redirect_map:
            issues.append({
                'url': url,
                'issue_type': 'redirect_chain',
                'severity': 'High',
                'detail': f"Redirect chain detected: {url} -> {target} (which also redirects)"
            })

    # 14. thin_content: Word Count < 200 on an indexable page
    # Severity: Low
    for _, row in df_html.iterrows():
        if is_indexable(row) and row['word_count'] < 200:
            issues.append({
                'url': row['url'],
                'issue_type': 'thin_content',
                'severity': 'Low',
                'detail': f"Thin content: {row['word_count']} words"
            })

    # 15. orphan_page: Inlinks = 0 on an indexable 200 page
    # Severity: Medium
    for _, row in df_idx200.iterrows():
        if row['inlinks'] == 0:
            issues.append({
                'url': row['url'],
                'issue_type': 'orphan_page',
                'severity': 'Medium',
                'detail': "Orphan page: 0 inlinks on an indexable 200 page."
            })

    # 16. non_indexable_but_linked: Indexability = Non-Indexable AND Inlinks > 0
    # Severity: Medium
    for _, row in df_html.iterrows():
        if str(row.get('indexable', '')).strip() == 'Non-Indexable' and row['inlinks'] > 0:
            issues.append({
                'url': row['url'],
                'issue_type': 'non_indexable_but_linked',
                'severity': 'Medium',
                'detail': f"Non-indexable page has {row['inlinks']} inlinks."
            })

    # 17. slow_page: Response Time > 1.0
    # Severity: Low
    for _, row in df_html.iterrows():
        if row['response_time'] > 1.0:
            issues.append({
                'url': row['url'],
                'issue_type': 'slow_page',
                'severity': 'Low',
                'detail': f"Slow page response time: {row['response_time']}s"
            })

    return issues

if __name__ == "__main__":
    # Quick test with dummy data
    data = {
        'url': ['/page1', '/page2', '/page3', '/page4'],
        'title': ['Title 1', 'Title 1', '', 'Short'],
        'meta_desc': ['Desc 1', 'Desc 1', 'Desc 2', ''],
        'h1': ['H1', 'H1', 'H1', 'H1'],
        'status_code': [200, 200, 200, 404],
        'word_count': [300, 300, 100, 50],
        'inlinks': [10, 10, 0, 5],
        'response_time': [0.5, 0.5, 1.5, 0.2],
        'indexable': ['Indexable', 'Indexable', 'Indexable', 'Indexable'],
        'content_type': ['text/html', 'text/html', 'text/html', 'text/html'],
        'title_pixel_width': [500, 500, 0, 100],
        'redirect_url': [None, None, None, None]
    }
    df = pd.DataFrame(data)
    results = audit(df)
    print(f"Found {len(results)} issues.")
    for res in results[:5]:
        print(res)
