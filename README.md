# Database Agent (FastMCP)

This repository hosts a lightweight FastMCP server that exposes sample SQLite data models to any Model Context Protocol (MCP) client. The server defined in `mcp_db_agent.py` provisions the schema on startup and registers tools for creating tables, inserting records, updating data, deleting rows, and inspecting table metadata.

## Highlights

- FastMCP-based server designed for quick experimentation.
- Automatic bootstrapping of the `students`, `teachers`, `products`, and `employees` tables.
- Tools for insert, update, delete, and query operations with dynamic column handling.
- Schema discovery helpers that report table structures and database metadata.

## Requirements

- Python 3.10+
- `uv` (recommended) or classic `pip`
- SQLite (bundled with Python)

## Installation

1. Clone the repository and switch into the project directory:

   ```bash
   git clone https://github.com/<user>/database-agent.git
   cd database-agent
   ```

2. Install dependencies:
   - With `uv`:

     ```bash
     uv sync
     ```

   - With `pip`:

     ```bash
     python -m venv .venv
     source .venv/bin/activate  # Windows: .venv\Scripts\activate
     pip install -r requirements.txt
     ```

## Running the Server

```bash
uv run python mcp_db_agent.py
# or
python mcp_db_agent.py
```

Once the server is running, register the definition in `mcp.json` with your MCP client to start invoking the tools.

## Available MCP Tools

- `insert_to_table(table_name, data)` – Inserts a row with column names inferred from `data`.
- `get_table_info(table_name)` – Returns the schema for the requested table.
- `list_all_tables()` – Lists every table present in the database.
- `query_table(table_name, limit)` – Retrieves the latest records.
- `delete_record(table_name, record_id)` – Removes a specific row.
- `update_record(table_name, record_id, data)` – Updates selected columns.

Each tool returns JSON payloads optimized for downstream MCP clients.

## Project Layout

```
mcp_db_agent.py   # FastMCP server and tool implementations
agent_database.db # Auto-created SQLite database file
README.md         # Project overview (this file)
pyproject.toml    # Project metadata and dependencies
requirements.txt  # pip dependency list
uv.lock           # uv lockfile
.gitignore        # VCS exclusions
LICENSE           # MIT license
mcp.json          # MCP client definition
```

## Development Notes

- Extend `init_database` with the schema definition for any new table you need.
- Register additional tools with the `@mcp.tool()` decorator and follow the existing patterns.
- When using `uv`, `uv run python mcp_db_agent.py` automatically honors the lockfile for reproducible environments.

## License

This project is distributed under the [MIT License](LICENSE).
