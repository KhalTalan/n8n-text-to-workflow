import os
import json
import re
import ast

def clean_description(description: str) -> str:
    """
    Removes boilerplate phrase: 'Follow technical documentation ...'
    Keeps only the part before it.
    """
    phrase = "Follow technical documentation"
    if phrase in description:
        description = description.split(phrase)[0].strip()
        # Remove trailing punctuation if left hanging
        description = description.rstrip(".;,- ")
    return description

def extract_metadata(file_path):
    """
    Extracts 'title', 'description', and 'contentType' from the front matter (--- ... ---) of a Markdown file.
    Returns a dict with title, description, contentType, and path.
    Returns None if front matter not found or missing title/description.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

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
                # fallback: split by comma
                content_type = [x.strip() for x in content_type_match.group(1).split(",")]

        # Clean up description
        description = clean_description(description_match.group(1).strip())

        return {
            "title": title_match.group(1).strip(),
            "description": description,
            "contentType": content_type,
            "path": file_path.replace("\\", "/")  # normalize path
        }

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def get_nodes_metadata(startpath):
    """
    Walks the docs folder and extracts metadata for all Markdown files.
    Returns a list of dicts: [{title, description, contentType, path}, ...]
    Skips files without title or description.
    """
    nodes = []

    for root, _, files in os.walk(startpath):
        for file in sorted(files):
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                meta = extract_metadata(full_path)
                if meta:  # only keep valid files
                    nodes.append(meta)

    return nodes

