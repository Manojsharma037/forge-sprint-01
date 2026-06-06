import pandas as pd
import sys

def ingest(file_path):
    """
    Reads a CSV file, flexibly matches and renames columns to a standardized set,
    and cleans the data by filling missing values.
    """
    # Mapping of standardized names to potential column name variations
    mapping = {
        'url': ['Address', 'URL', 'Page URL'],
        'title': ['Title 1', 'Page Title', 'Title'],
        'meta_desc': ['Meta Description 1', 'Meta Description', 'Description'],
        'h1': ['H1-1', 'H1', 'Main Heading'],
        'status_code': ['Status Code', 'HTTP Status'],
        'word_count': ['Word Count', 'Words'],
        'inlinks': ['Inlinks', 'Internal Links', 'In-links'],
        'response_time': ['Response Time', 'Time', 'Load Time'],
        'indexable': ['Indexability', 'Indexable', 'Robot Status']
    }

    # Read CSV
    df = pd.read_csv(file_path)
    current_cols = df.columns.tolist()
    rename_dict = {}

    # Flexible column matching
    for target, preferences in mapping.items():
        found = False
        for pref in preferences:
            # Search for an exact case-insensitive match first
            for col in current_cols:
                if pref.lower() == col.lower().strip():
                    rename_dict[col] = target
                    found = True
                    break
            if found: break

        if not found:
            for col in current_cols:
                if any(pref.lower() in col.lower() for pref in preferences):
                    rename_dict[col] = target
                    break

    # Rename columns
    df = df.rename(columns=rename_dict)

    # Ensure all target columns exist
    for target in mapping.keys():
        if target not in df.columns:
            df[target] = None

    # Keep only the requested columns
    df = df[list(mapping.keys())]

    # Fill missing values
    numeric_cols = ['status_code', 'word_count', 'inlinks', 'response_time']
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
        print(f"DataFrame Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print("\nFirst 2 rows:")
        print(df.head(2))
    except Exception as e:
        print(f"Error during ingestion: {e}")
        sys.exit(1)
