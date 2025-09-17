import os
from pathlib import Path
from tools.extract_schemas import run_schema_extraction
from tools.extract_docs import run_doc_extraction

def main():
    """
    The main function to orchestrate the data extraction process.
    """
    # Define paths relative to this script
    current_dir = Path(__file__).parent
    
    # Navigate up to the project's root folder (n8n-text-to-workflow)
    # The parent.parent logic is correct if 'n8n-text-to-workflow' is the project root
    # But since you have a parent folder 'text-to-workflow', we adjust the paths below
    
    # Get the parent directory of 'src', which is 'n8n-text-to-workflow'
    project_root = current_dir.parent
    
    # Now, find the submodule and data folders inside this 'n8n-text-to-workflow' folder
    n8n_core_dir = project_root / 'n8n-core'
    n8n_docs_core_dir = project_root / 'n8n-docs-core'
    data_dir = project_root / 'data'
    
    # Ensure data directory exists
    data_dir.mkdir(exist_ok=True)

    print("Starting data extraction...")
    
    # Run schema extraction first
    run_schema_extraction(str(n8n_core_dir), str(data_dir / 'schemas.json'))

    # Then run documentation extraction
    run_doc_extraction(str(n8n_docs_core_dir), str(data_dir))
    
    print("\nExtraction process completed.")

if __name__ == "__main__":
    main()