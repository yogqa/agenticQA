"""
Chaos Testing Scenario (Fuzzing)
================================

This script orchestrates a 'Shift-Left' Chaos/Fuzz testing workflow.

Workflow:
1.  **DatabaseAgent**: Fetches valid 'baseline' user data from the database.
2.  **ChaosAgent**:
    -   Receives the valid baseline data.
    -   Generates multiple 'negative' test scenarios (e.g., Missing Fields, Invalid Formats, Boundary Values).
    -   Produces a JSON list of malicious/invalid payloads.
3.  **APIAgent**:
    -   Iterates through the generated payloads.
    -   Executes them against the API Register endpoint.
    -   Captures the HTTP response codes.
4.  **ExcelAgent**: Logs the results (Payload vs Expected Status vs Actual Status) into a CSV file.

Goal: Identify if the API correctly handles invalid data (returns 400/422) or crashes/accepts it (500/200).
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from framework.agentFactory import AgentFactory
from autogen_agentchat.conditions import TextMentionTermination

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Verify API Key is set
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")

async def main():
    # Define model client
    model_client = OpenAIChatCompletionClient(model="gemini-2.5-flash")
    
    # Create Agent Factory
    factory = AgentFactory(model_client)
    
    # 1. Database Agent: Fetches valid baseline data
    database_agent = factory.create_database_agent(system_message=(
        "You are a Database specialist. "
        "Your task: "
        "1. List available tables "
        "2. Query 'RegistrationDetails' and 'UserNames' to get ONE SET of valid user data. "
        "3. Format this data as a clear JSON object. "
        "4. Output: 'BASELINE_DATA_READY' followed by the valid JSON. "
    ))

    # 2. Chaos Agent: Generates negative test cases
    chaos_agent = factory.create_chaos_agent(system_message=(
        "You are a QA Security Specialist (Chaos Agent). Your goal is to break the API. "
        "1. Wait for the 'BASELINE_DATA_READY' message from DatabaseAgent. "
        "2. Using that valid data as a base, generate 3 'negative' test scenarios for a User Registration API: "
        "   - Scenario A: Missing a required field (e.g., email or password). "
        "   - Scenario B: Invalid data format (e.g., email without '@'). "
        "   - Scenario C: Boundary case (e.g., extremely long name). "
        "3. Output MUST be a JSON list of objects, where each object has: "
        "   - 'test_type': description of the test "
        "   - 'payload': the actual JSON body to send "
        "   - 'expected_status': what HTTP status code you expect (e.g., 400). "
        "4. Say: 'CHAOS_DATA_READY' followed by your JSON list."
    ))

    # 3. API Agent: Executes the payloads
    api_agent = factory.create_api_agent(system_message=(
        "You are an API Tester. "
        "1. Wait for 'CHAOS_DATA_READY' from ChaosAgent. "
        "2. Read the Postman collection at framework/resources/EcomBasic.postman_collection.json to understand the Endpoint URL for 'register'. "
        "3. Iterate through EACH payload provided by ChaosAgent. "
        "4. For each payload: "
        "   - Make the POST request to the register endpoint. "
        "   - Capture the HTTP Status Code and the Response Message. "
        "5. Output a summary for ExcelAgent: "
        "   'TEST_EXECUTION_COMPLETE' "
        "   followed by a list of results: {test_type, sent_payload, actual_status_code, response_message}."
    ))

    # 4. Excel Agent: Logs results
    excel_agent = factory.create_excel_agent(system_message=(
        "You are a Reporting Specialist. "
        "1. Wait for 'TEST_EXECUTION_COMPLETE' from APIAgent. "
        "2. You MUST use the 'write_file' tool to write a CSV file. Do NOT use the excel tool. "
        "3. Create framework/resources/chaos_results.csv. "
        "4. Content should be a standard CSV with Headers: Test Type, Payload, Expected Status, Actual Status, Result (Pass/Fail). "
        "   - Pass means the API *rejected* the bad data (e.g. got 400 when expecting 400). "
        "   - Fail means the API accepted bad data (e.g. got 200). "
        "5. Example Row: 'Missing Email', '{...}', 400, 400, Pass "
        "6. ONLY say 'CHAOS REPORTING COMPLETE' after the tool has successfully returned."
    ))

    # Create Group Chat
    # Note: We use RoundRobin, but the system messages enforce the sequence.
    # We add a termination condition to stop exactly when the report is done.
    termination = TextMentionTermination("CHAOS REPORTING COMPLETE")

    team = RoundRobinGroupChat(
        participants=[database_agent, chaos_agent, api_agent, excel_agent],
        termination_condition=termination,
        max_turns=60
    )

    # Run the workflow
    task = "START_CHAOS_TESTING: DatabaseAgent, please fetch the baseline data."
    
    await Console(team.run_stream(task=task))

if __name__ == "__main__":
    asyncio.run(main())
