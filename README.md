# n8n-text-to-workflow

This project aims to convert natural language queries into executable n8n workflows using a multi-agent system.

### Project Structure
- `n8n-core/`: A Git submodule for the n8n source code. This is our source for node schemas and definitions.
- `n8n-docs-core/`: A Git submodule for the n8n documentation. This provides the human-readable documentation for each node.
- `data/`: Stores the JSON files extracted from the submodules, which our agents will use as "tools".
- `src/`: Contains the Python code for our agents, tools, and orchestration logic.

```
n8n-text-to-workflow/
├── .git/
├── n8n-core/                 # Git submodule: n8n source code (for node schemas)
├── n8n-docs-core/            # Git submodule: n8n documentation (for human-readable docs)
├── data/
│   ├── all_nodes_list.json   # A concise list of all available nodes for the planner agent.
│   ├── schemas.json          # Extracted JSON schemas for each node's parameters.
│   └── docs.json             # Extracted human-readable documentation for each node.
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner_agent.py
│   │   ├── node_json_agent.py
│   │   ├── connector_agent.py
│   │   └── supervisor_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── tools.py          # Contains the core functions for fetching data from 'data/' folder.
│   ├── __init__.py
│   └── main.py               # The main entry point for running the application.
├── pyproject.toml            # Used by 'uv' for dependency management.
├── requirements.txt          # Exported list of project dependencies.
└── README.md
```

### Getting Started

#### 1. Clone the repository and initialize submodules

This project uses Git submodules to pull the n8n source and documentation repositories.


(only once) # Add the n8n-io/n8n repository as a submodule 
(only once) # Add the n8n-io/n8n-docs repository as a submodule
```
git submodule add https://github.com/n8n-io/n8n.git n8n-core
git submodule add https://github.com/n8n-io/n8n-docs.git n8n-docs-core
```
(if need update) # Initialize and update the submodules
```
git submodule update --init --recursive
```


# Create a virtual environment named `.venv`
```
uv venv
```

# Activate the virtual environment
```
.venv\Scripts\activate.bat
```
