from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench
import shutil
import sys
import os


class McpConfig:

    @staticmethod
    def _ensure_command(cmd_name):
        """Return the path to the command if available, otherwise None."""
        return shutil.which(cmd_name)

    @staticmethod
    def get_mysql_workbench():
        # Use the current Python interpreter to improve portability
        python_exec = sys.executable or "python"
        mysql_server_params = StdioServerParams(
            command=python_exec,
            args=[
                "-m", "mysql_mcp_server.server"
            ],
            env={
                "MYSQL_HOST": "localhost",
                "MYSQL_PORT": "3306",
                "MYSQL_USER": "root",
                "MYSQL_PASSWORD": "mypassword",
                "MYSQL_DATABASE": "rahulshettyacademy"
            },
            read_timeout_seconds=30  # Increase timeout
        )
        return McpWorkbench(server_params=mysql_server_params)

    @staticmethod
    def get_rest_api_workbench():
        # npx is required for the rest api workbench. Provide a helpful error if it's missing.
        if not McpConfig._ensure_command("npx"):
            raise FileNotFoundError(
                "'npx' was not found on PATH. Please install Node.js (which provides npx) or add npx to PATH.\n"
                "You can download Node.js from https://nodejs.org/.")


        # Build the actual server params using npx
        rest_api_server_params = StdioServerParams(
            command="npx",
            args=[
                "-y",
                "dkmaker-mcp-rest-api"
            ],
            env={
                "REST_BASE_URL": "https://rahulshettyacademy.com",
                "HEADER_Accept": "application/json"
            },
            read_timeout_seconds=30
        )
        return McpWorkbench(server_params=rest_api_server_params)

    @staticmethod
    def get_excel_workbench():
        if not McpConfig._ensure_command("npx"):
            raise FileNotFoundError(
                "'npx' was not found on PATH. Please install Node.js (which provides npx) or add npx to PATH.\n"
                "You can download Node.js from https://nodejs.org/.")

        excel_server_params = StdioServerParams(
            command="npx",
            args=["--yes", "@negokaz/excel-mcp-server"],
            env={
                "EXCEL_MCP_PAGING_CELLS_LIMIT": "4000"
            },
            read_timeout_seconds=60
        )
        return McpWorkbench(server_params=excel_server_params)

    @staticmethod
    def get_filesystem_workbench():
        if not McpConfig._ensure_command("npx"):
            raise FileNotFoundError(
                "'npx' was not found on PATH. Please install Node.js (which provides npx) or add npx to PATH.\n"
                "You can download Node.js from https://nodejs.org/.")

        # Use the 'framework' directory within the project as the base path for files
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Ensure project root is also accessible if needed
        project_root = os.path.dirname(base_path)

        filesystem_server_params = StdioServerParams(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", base_path, project_root],
            read_timeout_seconds=60
        )
        return McpWorkbench(server_params=filesystem_server_params)