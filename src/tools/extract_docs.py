import os
import json
import re
import ast
from pathlib import Path

# --- Helper functions ---

def clean_description(description: str) -> str:
    """
    Removes boilerplate phrase: 'Follow technical documentation ...'
    Keeps only the part before it.
    """
    phrase = "Follow technical documentation"
    if phrase in description:
        description = description.split(phrase)[0].strip()
        description = description.rstrip(".;,- ")
    return description

def retrieve_file_content(file_path):
    """
    Retrieve the entire content of a file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def extract_metadata(file_path, base_folder):
    """
    Extracts 'title', 'description', and 'contentType' from Markdown front matter.
    Also retrieves the full file content.
    """
    content = retrieve_file_content(file_path)
    if content is None:
        return None

    # Match content between first pair of ---
    match = re.search(r'^---\s*(.*?)\s*---', content, re.DOTALL | re.MULTILINE)
    if not match:
        return None

    front_matter = match.group(1)

    # Extract fields
    title_match = re.search(r'^title:\s*(.+)$', front_matter, re.MULTILINE)
    description_match = re.search(r'^description:\s*(.+)$', front_matter, re.MULTILINE)
    content_type_match = re.search(r'^contentType:\s*\[(.*?)\]', front_matter, re.MULTILINE)

    # Skip if missing required fields
    if not title_match or not description_match:
        return None

    # Parse contentType as list
    content_type = []
    if content_type_match:
        raw = "[" + content_type_match.group(1).strip() + "]"
        try:
            content_type = ast.literal_eval(raw)
        except Exception:
            content_type = [x.strip() for x in content_type_match.group(1).split(",")]

    # Clean up description
    description = clean_description(description_match.group(1).strip())

    # Get the file path relative to the base folder
    rel_path = os.path.relpath(file_path, base_folder)
    
    return {
        "title": title_match.group(1).strip(),
        "description": description,
        "contentType": content_type,
        "path": rel_path.replace("\\", "/"),
        "file_content": content
    }

# --- Main function to be called from main.py ---
def run_doc_extraction(n8n_docs_dir, output_dir):
    """
    Extracts documentation metadata and full content for each node file.
    """
    docs_path = Path(n8n_docs_dir) / 'docs/integrations'
    if not docs_path.exists():
        print(f"Documentation directory not found: {docs_path}")
        return

    full_docs_list = []
    all_nodes_list = []

    print(f"Scanning documentation files in {docs_path}...")

    # Use os.walk for robust directory traversal
    for root, _, files in os.walk(docs_path):
        for file in sorted(files):
            if file == 'index.md':
                full_path = Path(root) / file
                
                meta = extract_metadata(str(full_path), str(docs_path))
                
                if meta:
                    # Append to the full docs list
                    full_docs_list.append(meta)

                    # Create a simplified entry for the all_nodes_list
                    all_nodes_list.append({
                        'title': meta['title'],
                        'description': meta['description'],
                        'path': meta['path']
                    })

    # Save the full documentation to docs.json
    docs_output_path = Path(output_dir) / 'docs.json'
    with open(docs_output_path, 'w', encoding='utf-8') as f:
        json.dump(full_docs_list, f, indent=2, ensure_ascii=False)
    print(f"Extracted documentation for {len(full_docs_list)} nodes to {docs_output_path}")

    # Save the simplified list of all nodes to all_nodes_list.json
    all_nodes_list_path = Path(output_dir) / 'all_nodes_list.json'
    with open(all_nodes_list_path, 'w', encoding='utf-8') as f:
        json.dump(all_nodes_list, f, indent=2, ensure_ascii=False)
    print(f"Extracted list of {len(all_nodes_list)} nodes to {all_nodes_list_path}")