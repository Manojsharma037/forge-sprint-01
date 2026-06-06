import pandas as pd
import sys

def ingest(file_path):
    mapping = {
        'url':               ['Address', 'URL', 'Page URL'],
        'title':             ['Title 1', 'Page Title', 'Title'],
        'title_length':      ['Title 1 Length', 'Title Length'],
        'meta_desc':         ['Meta Description 1', 'Meta Description', 'Description'],
        'meta_desc_length':  ['Meta Description 1 Length', 'Meta Description Length'],
        'h1':                ['H1-1', 'H1', 'Main Heading'],
        'status_code':       ['Status Code', 'HTTP Status'],
        'word_count':        ['Word Count', 'Words'],
        'inlinks':           ['Inlinks', 'Internal Links', 'In-links'],
        'response_time':     ['Response Time', 'Time', 'Load Time'],
        'indexable':         ['Indexability', 'Indexable', 'Robot Status'],
        'content_type':      ['Content Type', 'MIME Type'],
        'title_pixel_width': ['Title 1 Pixel Width', 'Title Pixel Width'],
        'redirect_url':      ['Redirect URL', 'Final URL'],
    }

    df = pd.read_csv(file_path, low_memory=False)
    current_cols = df.columns.tolist()
    rename_dict = {}

    for target, preferences in mapping.items():
        found = False
        for pref in preferences:
            for col in current_cols:
                if pref.lower() == col.lower().strip():
                    rename_dict[col] = target
                    found = True
                    break
            if found:
                break
        if not found:
            for col in current_cols:
                if any(pref.lower() in col.lower() for pref in preferences):
                    rename_dict[col] = target
                    break

    df = df.rename(columns=rename_dict)

    for target in mapping.keys():
        if target not in df.columns:
            df[target] = None

    df = df[list(mapping.keys())]

    numeric_cols = ['status_code', 'word_count', 'inlinks', 'response_time',
                    'title_pixel_width', 'title_length', 'meta_desc_length']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    text_cols = [col for col in df.columns if col not in numeric_cols]
    df[text_cols] = df[text_cols].fillna('')

    return df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide a CSV file path.")
        sys.exit(1)
    try:
        df = ingest(sys.argv[1])
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(df.head(2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)