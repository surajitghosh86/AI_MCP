`https://www.youtube.com/watch?v=kxB_SCXPQAY`


# Customer Management MCP Server

Flask REST API and MCP server for SQL Server `TestCustomer` CRUD.

## Claude Desktop setup

1. Install [uv](https://docs.astral.sh/uv/).
2. From this folder, install dependencies:

   ```powershell
   cd D:\Projects\MyProjects\AI_Projects\py_ApiWithSqlDb_MCP
   uv sync
   ```

3. Do **not** rely on `uv run mcp install mcp_server.py`. On this machine that
   command wrote a broken Claude entry: parent-repo `uv.EXE`, `--frozen`, and
   `mcp run` with no `--directory`. Claude then fails to start the server.

   Put the config below in `%APPDATA%\Claude\claude_desktop_config.json`.

4. Quit Claude Desktop completely (Task Manager if needed), then restart it.
5. You should see **CustomerManagement** tools in Claude.

## Manual Claude config (required)

`%APPDATA%\Claude\claude_desktop_config.json` should contain an entry like:

```json
"CustomerManagement": {
  "command": "C:\\Users\\WIN 11\\.local\\bin\\uv.exe",
  "args": [
    "run",
    "--directory",
    "D:\\Projects\\MyProjects\\AI_Projects\\py_ApiWithSqlDb_MCP",
    "python",
    "mcp_server.py"
  ]
}
```

`--directory` makes Claude use this project's `.venv` (mcp + pyodbc). Do not
use `uv run --frozen --with mcp[cli]` — that isolated env does not include
project modules, so the server never starts.

## Test locally

```powershell
uv run python mcp_client.py
uv run python mcp_client.py --tool get_customers
```

## Angular MCP client

The browser cannot spawn stdio, so run the same tools over Streamable HTTP:

```powershell
uv run python mcp_server.py --http
cd angular-mcp-client
npm start
```

Open http://localhost:4200. The app calls `http://127.0.0.1:8000/mcp` (`tools/list` and `tools/call`).

## Agent REST API

Run the agent API from this folder:

```powershell
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Send a `POST` request to `http://127.0.0.1:8000/api/agent/chat` with a JSON body
such as `{"message":"List customers"}`. Set `GEMINI_API_KEY` in the environment
or in a `.env` file in the project or repository root. If both
`GEMINI_API_KEY` and `GOOGLE_API_KEY` are set, the agent uses `GEMINI_API_KEY`.
Restart the API process after changing the key. This API also uses port 8000,
so do not run it at the same time as the MCP HTTP server.

## Flask API

```powershell
uv run python app.py
```

## Notes

- SQL Server ODBC driver must be installed for database tools to work.
- DB connection settings are in `dbHelper.py`.


`uv run --active mcp install mcp_server.py`


#SQL
create proc GetTestCustomerDetails
as
	SELECT * FROM TestCustomer
GO

create proc GetTestCustomerDetailsById
@Id int
as
	SELECT * FROM TestCustomer WHERE Id = @Id;
GO

create proc AddTestCustomerDetails
@FirstName varchar(100)
,@LastName varchar(100)
as
	INSERT INTO TestCustomer (FirstName, LastName) 
	VALUES (@FirstName, @LastName);
GO

create proc UpdateTestCustomerDetails
@Id int
,@FirstName varchar(100)
,@LastName varchar(100)
AS
	UPDATE TestCustomer 
	SET FirstName = @FirstName, LastName = @LastName
	WHERE Id = @Id;
GO

create proc DeleteTestCustomerDetails
@Id int
AS
	DELETE FROM TestCustomer WHERE Id = @Id;
