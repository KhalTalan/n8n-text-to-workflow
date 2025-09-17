import os
import json
from pathlib import Path
import re

# --- Helper functions ---

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return None

def safe_float(s):
    try:
        return float(s)
    except Exception:
        return None

def normalize_node_basename(stem):
    return stem[:-5] if stem.endswith('.node') else stem

def resolve_import_path(base_file, import_path):
    base_dir = Path(base_file).parent
    candidate = (base_dir / import_path)
    for ext in ['', '.ts', '.node.ts', '/index.ts', '/index.node.ts']:
        p = Path(str(candidate) + ext)
        if p.exists():
            return str(p)
    if not import_path.endswith('.ts'):
        for ext in ext in ['.ts', '.node.ts']:
            p = base_dir / (import_path + ext)
            if p.exists():
                return str(p)
    return None

def clean_multiline_string(s):
    return re.sub(r'\s+', ' ', s.strip())

# --- Extraction functions (updated to extract operations and resources) ---

def extract_base_description(content):
    result = {}
    m = re.search(r'const\s+baseDescription\s*:[^{=]*= \s*\{(.*?)\}\s*;', content, re.DOTALL)
    if not m:
        m = re.search(r'const\s+baseDescription\s*=\s*\{(.*?)\}\s*;', content, re.DOTALL)
    if not m:
        return result
    block = m.group(1)

    patterns = {
        'displayName': r"displayName\s*:\s*(['\"])(.*?)\1",
        'name': r"name\s*:\s*(['\"])(.*?)\1",
        'subtitle': r"subtitle\s*:\s*'((?:\\'|[^'])*?)'",
        'description': r"description\s*:\s*(['\"])(.*?)\1",
        'group': r"group\s*:\s*\[([^\]]+)\]",
        'defaultVersion': r"defaultVersion\s*:\s*([\d\.]+)"
    }

    for key, regex in patterns.items():
        mm = re.search(regex, block, re.DOTALL)
        if mm:
            if key == 'group':
                groups = mm.group(1).split(',')
                result['group'] = [s.strip().strip('\"\'') for s in groups]
            elif key == 'defaultVersion':
                result['defaultVersion'] = safe_float(mm.group(1))
            else:
                if mm.lastindex and mm.lastindex >= 2:
                    result[key] = mm.group(2)
                else:
                    result[key] = mm.group(1)
    return result

def extract_single_node_fields(content):
    result = {}
    patterns = {
        'group': r"group\s*:\s*\[([^\]]+)\]",
        'version': r"version\s*:\s*([\d\.]+)",
        'description': r"description\s*:\s*(['\"])(.*?)\1",
        'inputs': r"inputs\s*:\s*\[([^\]]*)\]",
        'outputs': r"outputs\s*:\s*\[([^\]]*)\]",
        'credentials': r"credentials\s*:\s*\[([^\]]*)\]",
        'webhooks': r"webhooks\s*:\s*\[([^\]]*)\]"
    }

    for key, regex in patterns.items():
        mm = re.search(regex, content, re.DOTALL)
        if mm:
            if key in ['group']:
                groups = mm.group(1).split(',')
                result[key] = [s.strip().strip('\'"') for s in groups]
            elif key in ['version']:
                result[key] = safe_float(mm.group(1))
            elif key in ['inputs', 'outputs', 'credentials', 'webhooks']:
                result[key] = clean_multiline_string(mm.group(1))
            elif key == 'description':
                result[key] = mm.group(2).strip() if mm.lastindex and mm.lastindex >= 2 else mm.group(1).strip()
            else:
                result[key] = mm.group(1).strip()
    return result

def extract_node_versions(content):
    versions = []
    m = re.search(r'const\s+nodeVersions\s*:[^{=]*= \s*\{(.*?)\}\s*;', content, re.DOTALL)
    if not m:
        m = re.search(r'const\s+nodeVersions\s*=\s*\{(.*?)\}\s*;', content, re.DOTALL)
    if m:
        block = m.group(1)
        for km in re.finditer(r"['\"]?(\d+(?:\.\d+)?)['\"]?\s*:", block):
            v = safe_float(km.group(1))
            if v is not None and v not in versions:
                versions.append(v)
    return sorted(versions)

def find_version_imports(content):
    imports = []
    for im in re.finditer(r"import\s+\{[^}]+\}\s+from\s+['\"](.+?)['\"]\s*;", content):
        path = im.group(1)
        if '/v' in path or path.endswith('.node') or '/v1' in path or '/v2' in path:
            imports.append(path)
    return imports

def extract_properties_from_content(content):
    props = []
    seen_names = set()
    for pm in re.finditer(r"\{([^}]*displayName\s*:\s*['\"][^'\"]+['\"][^}]*)\}", content, re.DOTALL):
        block = pm.group(0)
        name = re.search(r"name\s*:\s*['\"]([^'\"]+)['\"]", block)
        if name:
            name = name.group(1)
            if name and name not in seen_names:
                prop = parse_property_block(block)
                if prop and prop.get('name'):
                    props.append(prop)
                    seen_names.add(prop['name'])
    if not props:
        for m in re.finditer(r"name\s*:\s*(['\"])([^'\"]+?)\1", content, re.DOTALL):
            name = m.group(2)
            if name and name not in seen_names:
                props.append({'name': name, 'type': 'string', 'description': 'Extract manually if needed'})
                seen_names.add(name)
    return props

def parse_property_block(block):
    p = {}
    m = re.search(r"name\s*:\s*(['\"])(.*?)\1", block, re.DOTALL)
    if m: p['name'] = m.group(2)
    m = re.search(r"displayName\s*:\s*(['\"])(.*?)\1", block, re.DOTALL)
    if m: p['displayName'] = m.group(2)
    m = re.search(r"type\s*:\s*(['\"])(.*?)\1", block, re.DOTALL)
    if m: p['type'] = m.group(2)
    m = re.search(r"default\s*:\s*(['\"])(.*?)\1", block, re.DOTALL)
    if m: p['default'] = m.group(2)
    else:
        m = re.search(r"default\s*:\s*([0-9\.]+)", block)
        if m: p['default'] = m.group(1)
    m = re.search(r"required\s*:\s*(true|false)", block)
    if m: p['required'] = (m.group(1) == 'true')
    m = re.search(r"description\s*:\s*(['\"]) ([\s\S]*?)\1(?=\s*,|\s*\})", block, re.DOTALL)
    if m: p['description'] = m.group(2)
    m = re.search(r"placeholder\s*:\s*(['\"])(.*?)\1", block, re.DOTALL)
    if m: p['placeholder'] = m.group(2)

    # Updated to extract options
    m = re.search(r"options\s*:\s*\[([\s\S]*?)\]", block, re.DOTALL)
    if m:
        options_str = m.group(1)
        options = []
        option_matches = re.finditer(r"\{([\s\S]*?)\}", options_str, re.DOTALL)
        for opt_m in option_matches:
            opt_block = opt_m.group(1)
            opt = {}
            opt_name = re.search(r"name\s*:\s*(['\"])(.*?)\1", opt_block, re.DOTALL)
            if opt_name: opt['name'] = opt_name.group(2)
            opt_value = re.search(r"value\s*:\s*(['\"])(.*?)\1", opt_block, re.DOTALL)
            if opt_value: opt['value'] = opt_value.group(2)
            opt_desc = re.search(r"description\s*:\s*(['\"])(.*?)\1", opt_block, re.DOTALL)
            if opt_desc: opt['description'] = opt_desc.group(2)
            opt_action = re.search(r"action\s*:\s*(['\"])(.*?)\1", opt_block, re.DOTALL)
            if opt_action: opt['action'] = opt_action.group(2)
            if opt:
                options.append(opt)
        if options:
            p['options'] = options

    # Updated to extract typeOptions
    m = re.search(r"typeOptions\s*:\s*\{([\s\S]*?)\}", block, re.DOTALL)
    if m:
        type_options_str = m.group(1)
        type_options = {}
        type_min = re.search(r"minValue\s*:\s*(\d+)", type_options_str)
        if type_min: type_options['minValue'] = int(type_min.group(1))
        type_max = re.search(r"maxValue\s*:\s*(\d+)", type_options_str)
        if type_max: type_options['maxValue'] = int(type_max.group(1))
        if type_options:
            p['typeOptions'] = type_options

    return p if p else None

# --- Main function to be called from main.py ---

def run_schema_extraction(n8n_core_dir, output_file_path):
    """
    Main function to scan node files and extract schemas.
    """
    nodes_dir = Path(n8n_core_dir) / 'packages'
    if not nodes_dir.exists():
        print(f"Nodes directory not found: {nodes_dir}")
        return

    schemas = {}
    node_files = list(nodes_dir.rglob('*.node.ts'))
    print(f"Scanning {len(node_files)} node files...")

    for file_path in node_files:
        try:
            info = deep_extract_node_info(file_path)
            key = normalize_node_basename(Path(file_path).stem)
            schemas[key] = info
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(schemas, f, indent=2, ensure_ascii=False)

    print(f"Extraction complete. {len(schemas)} nodes saved to {output_file_path}")

def deep_extract_node_info(file_path):
    file_path = str(file_path)
    node_stem = Path(file_path).stem
    node_base = normalize_node_basename(node_stem)
    content = read_file(file_path) or ""

    result = {
        'name': node_base,
        'displayName': node_base,
        'type': f"n8n-nodes-base.{node_base}",
        'subtitle': None,
        'description': None,
        'group': [],
        'defaultVersion': 1,
        'availableVersions': [],
        'inputs': [],
        'outputs': [],
        'credentials': [],
        'webhooks': [],
        'properties': []
    }

    base_fields = extract_base_description(content)
    if base_fields:
        for k, v in base_fields.items():
            if v is not None:
                result[k] = v

    versions = extract_node_versions(content)
    if versions:
        result['availableVersions'] = versions
        if not result.get('defaultVersion') or result.get('defaultVersion') == 1:
            result['defaultVersion'] = max(versions)

    single_fields = extract_single_node_fields(content)
    if single_fields:
        for k, v in single_fields.items():
            if v is not None:
                result[k] = v

    if not result.get('subtitle'):
        mm = re.search(r"subtitle\s*:\s*'((?:\\'|[^'])*?)'", content, re.DOTALL)
        if mm:
            result['subtitle'] = mm.group(1)

    imports = find_version_imports(content)
    combined_content = content
    for imp_path in imports:
        resolved = resolve_import_path(file_path, imp_path)
        if resolved:
            vcont = read_file(resolved)
            if vcont:
                combined_content += "\n\n// --- imported: " + imp_path + " --- \n\n" + vcont

    props = extract_properties_from_content(combined_content)
    result['properties'] = props if props else [{'name': 'TODO_add_property', 'type': 'string', 'description': 'Fill manually if needed'}]

    for key in ['inputs', 'outputs', 'credentials', 'webhooks']:
        if key in result and result[key]:
            result[key] = clean_multiline_string(result[key])

    return result
