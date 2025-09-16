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
├── n8n-core/                 # Git submodule for n8n source code
├── n8n-docs-core/            # Git submodule for n8n docs
├── data/
│   ├── schemas.json          # Extracted node schemas (from n8n-core)
│   ├── docs.json             # Extracted node documentation (from n8n-docs-core)
│   └── all_nodes_list.json   # A list of all available nodes for the planner
├── src/
│   ├── agents/
│   │   ├── planner_agent.py
│   │   └── ... (other agents)
│   ├── tools/
│   │   └── tools.py          # Our tools implementation file
│   └── __init__.py
└── README.md
```

### Getting Started

#### 1. Clone the repository and initialize submodules

This project uses Git submodules to pull the n8n source and documentation repositories.

```
------------------------------------------------------------
(only once) # Add the n8n-io/n8n repository as a submodule 
git submodule add https://github.com/n8n-io/n8n.git n8n-core

(only once) # Add the n8n-io/n8n-docs repository as a submodule
git submodule add https://github.com/n8n-io/n8n-docs.git n8n-docs-core

(if need update) # Initialize and update the submodules
git submodule update --init --recursive
------------------------------------------------------------
# Create a virtual environment named `.venv`
uv venv

# Activate the virtual environment
.venv\Scripts\activate.bat   # On Windows
------------------------------------------------------------

```
