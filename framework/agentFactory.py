from autogen_agentchat.agents import AssistantAgent

from framework.mcp_config import McpConfig


class AgentFactory:
    """
    Factory for creating specialized agents with predefined roles and toolsets.

    This factory handles the initialization of AssistantAgents, injecting the
    appropriate MCP workbench tools (MySQL, REST API, Filesystem, Excel) based
    on the agent's purpose.
    """

    def __init__(self, model_client):
        """
        Args:
            model_client: The LLM model client (e.g., OpenAIChatCompletionClient)
                         that agents will use for inference.
        """
        self.model_client = model_client
        self.mcp_config = McpConfig()

    def create_database_agent(self, system_message):
        """Creates an agent connected to the MySQL Database."""
        return AssistantAgent(
            name="DatabaseAgent",
            model_client=self.model_client,
            workbench=self.mcp_config.get_mysql_workbench(),
            system_message=system_message
        )

    def create_api_agent(self, system_message):
        """
        Creates an agent capable of making REST API calls and reading local files.
        Connects to both REST API and Filesystem workbenches.
        """
        rest_api_workbench = self.mcp_config.get_rest_api_workbench()
        file_system_workbench = self.mcp_config.get_filesystem_workbench()

        # Requires multiple workbenches to read Postman collections and fire requests
        api_agent = AssistantAgent(
            name="APIAgent",
            model_client=self.model_client,
            workbench=[rest_api_workbench, file_system_workbench],
            system_message=system_message
        )
        return api_agent

    def create_excel_agent(self, system_message=None):
        """
        Creates an agent for reporting.
        Connects to Excel and Filesystem tools to read/write results (CSV/Excel).
        """
        excel_workbench = self.mcp_config.get_excel_workbench()
        file_system_workbench = self.mcp_config.get_filesystem_workbench()

        return AssistantAgent(
            name="ExcelAgent",
            model_client=self.model_client,
            workbench=[excel_workbench, file_system_workbench],
            system_message=system_message
        )

    def create_chaos_agent(self, system_message: str) -> AssistantAgent:
        """
        Creates the Chaos Agent.
        This agent is purely generative (logic-based) and does not require external tools,
        as its job is to invent bad scenarios based on good data.
        """
        return AssistantAgent(
            name="ChaosAgent",
            model_client=self.model_client,
            system_message=system_message
        )


