"""
User Registration Scenario
==========================

This script orchestrates the 'Happy Path' for User Registration.

Workflow:
1.  **DatabaseAgent**: Connects to the MySQL database to fetch schema information and a sample of
    user data (from 'RegistrationDetails' and 'UserNames' tables) to understand valid data structures.
2.  **APIAgent**:
    -   Reads the Postman Collection (`EcomBasic.postman_collection.json`) to find the Register endpoint.
    -   Constructs a valid registration payload based on the Database Agent's findings.
    -   Sends a POST request to the API.
3.  **ExcelAgent**: Logs the successful registration details into an Excel/CSV file for reporting.

Agents use a RoundRobinGroupChat to coordinate their actions sequentially.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv

from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from framework.agentFactory import AgentFactory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")

async def main():
    model_client = OpenAIChatCompletionClient( model="gemini-2.5-flash" )
    factory = AgentFactory( model_client )
    database_agent = factory.create_database_agent( system_message=("""
            You are a Database specialist responsible for retrieving user registration data.

            Your task:
            1. Connect to the MySQL database 'rahulshettyacademy'
            2. Query the 'RegistrationDetails' table to get a random record
            3. List available tables to confirm table names if needed
            4. Query the 'Usernames' table (or similar) to get additional user data
            4. Combine the data from both tables to create complete registration information
            5. Ensure the email is unique by adding a timestamp or random number if needed
            6. Prepare all the registration data in a structured format so that another agent can understand
            When ready, write: "DATABASE_DATA_READY - APIAgent should proceed next"
            """) )


            CRITICAL: Only save data if APIAgent reports successful login, not just attempted login.

            When complete, write: "REGISTRATION PROCESS COMPLETE" and stop.
            """) )

    team = RoundRobinGroupChat( participants=[database_agent, api_agent, excel_agent],
                                termination_condition=TextMentionTermination( "REGISTRATION PROCESS COMPLETE" ) )

    task_result = await Console( team.run_stream( task="Execute Sequential User Registration Process:\n\n"

                                                       "STEP 1 - DatabaseAgent (FIRST):\n"
                                                       "Get random registration data from database tables and format it clearly.\n\n"

                                                       "STEP 2 - APIAgent:\n"
                                                       "Read Postman collection files, then make registration followed by login APIs using the database data.\n\n"

                                                       "STEP 3 - ExcelAgent:\n"
                                                       "Save successful registration login details to Excel file.\n\n"

                                                       "Each agent should complete their work fully before the next agent begins. "
                                                       "Pass data clearly between agents using the specified formats." ) )
    final_message = task_result.messages[-1]
    final_message.content





asyncio_run_guard = """
Wrap asyncio.run(main()) in a try/except to ensure we print any exceptions and tracebacks
so failures from child libraries show up clearly in the console.
"""

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        import traceback
        traceback.print_exc()
