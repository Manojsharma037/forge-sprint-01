import pandas as pd
import sys
from ingest import ingest

def audit(df):
    issues = []

    # Only HTML pages
    if 'content_type' in df.columns:
        df = df[df['content_type'].str.contains('text/html', na=False, case=False)].copy()
    else:
        df = df.copy()

    # Ensure all columns exist
    for col in ['url','title','meta_desc','h1','status_code','word_count',
                'inlinks','response_time','indexable','title_pixel_width','redirect_url']:
        if col not in df.columns:
            df[col] = None

    # Clean types
    df['status_code']       = pd.to_numeric(df['status_code'], errors='coerce').fillna(0)
    df['word_count']        = pd.to_numeric(df['word_count'], errors='coerce').fillna(0)
    df['inlinks']           = pd.to_numeric(df['inlinks'], errors='coerce').fillna(0)
    df['response_time']     = pd.to_numeric(df['response_time'], errors='coerce').fillna(0)
    df['title_pixel_width'] = pd.to_numeric(df['title_pixel_width'], errors='coerce').fillna(0)
    for col in ['url','title','meta_desc','h1','indexable','redirect_url']:
        df[col] = df[col].fillna('').astype(str)

    # Indexable 200 subset
    df_idx200 = df[(df['status_code'] == 200) & (df['indexable'].str.strip() == 'Indexable')]

    # Pre-calculate duplicates
    def get_dupes(subset, col):
        counts = subset[subset[col].str.strip() != ''][col].value_counts()
        return set(counts[counts >= 2].index)

    dupe_titles = get_dupes(df_idx200, 'title')
    dupe_metas  = get_dupes(df_idx200, 'meta_desc')
    dupe_h1s    = get_dupes(df_idx200, 'h1')

    # Redirect map for chain detection
    redirects = df[df['status_code'].between(300, 399)]
    redirect_map = dict(zip(redirects['url'], redirects['redirect_url']))

    # Main loop
    for _, row in df.iterrows():
        url       = row['url']
        status    = int(row['status_code'])
        title     = str(row['title']).strip()
        meta      = str(row['meta_desc']).strip()
        h1        = str(row['h1']).strip()
        indexable = str(row['indexable']).strip()
        words     = row['word_count']
        inlinks   = row['inlinks']
        resp_time = row['response_time']
        pixel_w   = row['title_pixel_width']
        is_idx200 = (status == 200 and indexable == 'Indexable')

        # 1. missing_title
        if is_idx200 and not title:
            issues.append({'url': url, 'issue_type': 'missing_title',
                'severity': 'high', 'detail': 'Title missing on indexable 200 page'})

        # 2. duplicate_title
        if is_idx200 and title in dupe_titles:
            issues.append({'url': url, 'issue_type': 'duplicate_title',
                'severity': 'high', 'detail': f'Duplicate title: {title}'})

        # 3. title_too_long
        if pixel_w > 561 or len(title) > 60:
            issues.append({'url': url, 'issue_type': 'title_too_long',
                'severity': 'medium', 'detail': f'Title too long (len:{len(title)}, px:{pixel_w})'})

        # 4. title_too_short
        if 0 < len(title) < 30:
            issues.append({'url': url, 'issue_type': 'title_too_short',
                'severity': 'low', 'detail': f'Title too short (len:{len(title)})'})

        # 5. missing_meta_description
        if is_idx200 and not meta:
            issues.append({'url': url, 'issue_type': 'missing_meta_description',
                'severity': 'medium', 'detail': 'Meta description missing on indexable 200 page'})

        # 6. duplicate_meta_description
        if is_idx200 and meta in dupe_metas:
            issues.append({'url': url, 'issue_type': 'duplicate_meta_description',
                'severity': 'medium', 'detail': f'Duplicate meta: {meta[:50]}'})

        # 7. meta_description_too_long
        if len(meta) > 155:
            issues.append({'url': url, 'issue_type': 'meta_description_too_long',
                'severity': 'low', 'detail': f'Meta too long (len:{len(meta)})'})

        # 8. missing_h1
        if status == 200 and not h1:
            issues.append({'url': url, 'issue_type': 'missing_h1',
                'severity': 'medium', 'detail': 'H1 missing on 200 page'})

        # 9. duplicate_h1
        if is_idx200 and h1 in dupe_h1s:
            issues.append({'url': url, 'issue_type': 'duplicate_h1',
                'severity': 'low', 'detail': f'Duplicate H1: {h1}'})

        # 10. broken_link
        if 400 <= status < 500:
            issues.append({'url': url, 'issue_type': 'broken_link',
                'severity': 'high', 'detail': f'Broken link: {status}'})

        # 11. server_error
        if 500 <= status < 600:
            issues.append({'url': url, 'issue_type': 'server_error',
                'severity': 'high', 'detail': f'Server error: {status}'})

        # 12. redirect
        if 300 <= status < 400:
            issues.append({'url': url, 'issue_type': 'redirect',
                'severity': 'medium', 'detail': f'Redirect: {status}'})

        # 13. redirect_chain
        target = redirect_map.get(url, '')
        if target and target in redirect_map:
            issues.append({'url': url, 'issue_type': 'redirect_chain',
                'severity': 'high', 'detail': f'Chain: {url} -> {target} -> ...'})

        # 14. thin_content
        if indexable == 'Indexable' and words < 200:
            issues.append({'url': url, 'issue_type': 'thin_content',
                'severity': 'low', 'detail': f'Only {int(words)} words'})

        # 15. orphan_page
        if is_idx200 and inlinks == 0:
            issues.append({'url': url, 'issue_type': 'orphan_page',
                'severity': 'medium', 'detail': '0 inlinks on indexable 200 page'})

        # 16. non_indexable_but_linked
        if indexable == 'Non-Indexable' and inlinks > 0:
            issues.append({'url': url, 'issue_type': 'non_indexable_but_linked',
                'severity': 'medium', 'detail': f'Non-indexable but has {int(inlinks)} inlinks'})

        # 17. slow_page
        if resp_time > 1.0:
            issues.append({'url': url, 'issue_type': 'slow_page',
                'severity': 'low', 'detail': f'Response time: {resp_time}s'})

    return issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit.py <csv_path>")
        sys.exit(1)
    df = ingest(sys.argv[1])
    results = audit(df)
    print(f"Found {len(results)} issues")
    for r in results[:5]:
        print(r)