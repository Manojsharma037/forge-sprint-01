import pandas as pd

def audit(df):
    """
    Performs a comprehensive SEO audit based on the Rulebook.
    Detects 17 deterministic issues and returns a list of dicts.
    """
    issues = []

    # --- Pre-processing & Setup ---
    # Rule: Only consider rows where `Content Type` contains `text/html`
    if 'content_type' in df.columns:
        df = df[df['content_type'].str.contains('text/html', na=False, case=False)].copy()

    # Standardize key columns to avoid KeyErrors
    cols = {
        'url': 'url',
        'title': 'title',
        'meta_desc': 'meta_desc',
        'h1': 'h1',
        'status': 'status_code',
        'words': 'word_count',
        'inlinks': 'inlinks',
        'time': 'response_time',
        'idx': 'indexable',
        'pixel_w': 'title_pixel_width',
        'red_url': 'redirect_url'
    }

    # Ensure these columns exist in the dataframe, filling with defaults if missing
    for col_name in cols.values():
        if col_name not in df.columns:
            df[col_name] = None

    # Helper: Identify indexable 200 pages (needed for several rules)
    is_indexable_200 = (
        (df[cols['status']] == 200) &
        (df[cols['idx']].astype(str).str.strip() == 'Indexable')
    )
    df_idx200 = df[is_indexable_200]

    # Pre-calculate duplicates for Indexable 200 pages
    # We only count non-empty strings as potential duplicates
    def get_dupes(subset, col):
        counts = subset[subset[col].astype(str).str.strip() != ''][col].value_counts()
        return set(counts[counts >= 2].index)

    dupe_titles = get_dupes(df_idx200, cols['title'])
    dupe_metas = get_dupes(df_idx200, cols['meta_desc'])
    dupe_h1s = get_dupes(df_idx200, cols['h1'])

    # Map for redirect chain detection: {URL -> Redirect URL}
    redirect_map = df[df[cols['status']].between(300, 399)].set_index(cols['url'])[cols['red_url']].to_dict()

    # --- Rule Execution ---
    for _, row in df.iterrows():
        url = row[cols['url']]
        status = row[cols['status']]
        title = str(row[cols['title']] if pd.notnull(row[cols['title']]) else '')
        meta = str(row[cols['meta_desc']] if pd.notnull(row[cols['meta_desc']]) else '')
        h1 = str(row[cols['h1']] if pd.notnull(row[cols['h1']]) else '')
        indexable = str(row[cols['idx']]).strip()
        words = row[cols['words']]
        inlinks = row[cols['inlinks']]
        time = row[cols['time']]
        pixel_w = row[cols['pixel_w']]

        # Check if this row is an indexable 200 page
        is_idx200 = (status == 200 and indexable == 'Indexable')

        # 1. missing_title | High
        if is_idx200 and not title.strip():
            issues.append({'url': url, 'issue_type': 'missing_title', 'severity': 'High', 'detail': 'Title is missing on an indexable 200 page'})

        # 2. duplicate_title | High
        if is_idx200 and title.strip() in dupe_titles:
            issues.append({'url': url, 'issue_type': 'duplicate_title', 'severity': 'High', 'detail': f'Duplicate title: {title}'})

        # 3. title_too_long | Medium
        if (pd.notnull(pixel_w) and pixel_w > 561) or len(title) > 60:
            issues.append({'url': url, 'issue_type': 'title_too_long', 'severity': 'Medium', 'detail': f'Title too long (Len: {len(title)}, Px: {pixel_w})'})

        # 4. title_too_short | Low
        if 0 < len(title) < 30:
            issues.append({'url': url, 'issue_type': 'title_too_short', 'severity': 'Low', 'detail': f'Title too short (Len: {len(title)})'})

        # 5. missing_meta_description | Medium
        if is_idx200 and not meta.strip():
            issues.append({'url': url, 'issue_type': 'missing_meta_description', 'severity': 'Medium', 'detail': 'Meta description is missing on an indexable 200 page'})

        # 6. duplicate_meta_description | Medium
        if is_idx200 and meta.strip() in dupe_metas:
            issues.append({'url': url, 'issue_type': 'duplicate_meta_description', 'severity': 'Medium', 'detail': f'Duplicate meta description: {meta}'})

        # 7. meta_description_too_long | Low
        if len(meta) > 155:
            issues.append({'url': url, 'issue_type': 'meta_description_too_long', 'severity': 'Low', 'detail': f'Meta description too long (Len: {len(meta)})'})

        # 8. missing_h1 | Medium
        if status == 200 and not h1.strip():
            issues.append({'url': url, 'issue_type': 'missing_h1', 'severity': 'Medium', 'detail': 'H1 is missing on a 200 page'})

        # 9. duplicate_h1 | Low
        if is_idx200 and h1.strip() in dupe_h1s:
            issues.append({'url': url, 'issue_type': 'duplicate_h1', 'severity': 'Low', 'detail': f'Duplicate H1: {h1}'})

        # 10. broken_link | High
        if 400 <= status < 500:
            issues.append({'url': url, 'issue_type': 'broken_link', 'severity': 'High', 'detail': f'Broken link: {status}'})

        # 11. server_error | High
        if 500 <= status < 600:
            issues.append({'url': url, 'issue_type': 'server_error', 'severity': 'High', 'detail': f'Server error: {status}'})

        # 12. redirect | Medium
        if 300 <= status < 400:
            issues.append({'url': url, 'issue_type': 'redirect', 'severity': 'Medium', 'detail': f'Redirect: {status}'})

        # 13. redirect_chain | High
        target_url = redirect_map.get(url)
        if target_url and target_url in redirect_map:
            issues.append({'url': url, 'issue_type': 'redirect_chain', 'severity': 'High', 'detail': f'Redirect chain: {url} -> {target_url} (also redirects)'})

        # 14. thin_content | Low
        if indexable == 'Indexable' and (pd.notnull(words) and words < 200):
            issues.append({'url': url, 'issue_type': 'thin_content', 'severity': 'Low', 'detail': f'Thin content: {words} words'})

        # 15. orphan_page | Medium
        if is_idx200 and (pd.notnull(inlinks) and inlinks == 0):
            issues.append({'url': url, 'issue_type': 'orphan_page', 'severity': 'Medium', 'detail': 'Orphan page: 0 inlinks on indexable 200 page'})

        # 16. non_indexable_but_linked | Medium
        if indexable == 'Non-Indexable' and (pd.notnull(inlinks) and inlinks > 0):
            issues.append({'url': url, 'issue_type': 'non_indexable_but_linked', 'severity': 'Medium', 'detail': f'Non-indexable page has {inlinks} inlinks'})

        # 17. slow_page | Low
        if pd.notnull(time) and time > 1.0:
            issues.append({'url': url, 'issue_type': 'slow_page', 'severity': 'Low', 'detail': f'Slow response time: {time}s'})

    return issues

if __name__ == "__main__":
    # Basic Test
    data = {
        'url': ['/p1', '/p2', '/p3'],
        'title': ['', 'Same', 'Same'],
        'status_code': [200, 200, 404],
        'indexable': ['Indexable', 'Indexable', 'Indexable'],
        'word_count': [100, 300, 300],
        'inlinks': [0, 5, 5]
    }
    df_test = pd.DataFrame(data)
    res = audit(df_test)
    print(f"Found {len(res)} issues.")
    for item in res:
        print(item)
