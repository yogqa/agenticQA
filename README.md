# AgenticQA Framework

**Next-Generation Automated Testing with Collaborative AI Agents**

## 🚀 Project Overview

The **AgenticQA Framework** is a cutting-edge proof-of-concept demonstrating the power of **Multi-Agent Systems (MAS)** in software quality assurance. Unlike traditional automation scripts that follow rigid, linear paths, this framework employs autonomous AI agents that collaborate, reason, and adapt to perform complex testing tasks.

By leveraging the "Shift-Left" philosophy, we move testing earlier in the lifecycle—generating data, fuzzing inputs, and validating API contracts before a human tester ever needs to intervene.

## 🤖 The Multi-Agentic Approach

We move beyond simple LLM prompts by orchestrating a team of specialized agents, each with a distinct role and toolset (Model Context Protocol - MCP).

### The Agent Team
1.  **Database Agent (The Oracle)**:
    *   **Role**: Source of Truth.
    *   **Capabilities**: Connects directly to the MySQL database to inspect schema, fetch valid baseline data, and verify data persistence.
    *   **Tooling**: MySQL MCP Server.

2.  **Chaos Agent (The Adversary)**:
    *   **Role**: Security & Robustness Tester.
    *   **Capabilities**: Fuzz testing engine. Takes valid data and intelligently corrupts it (e.g., SQL injection patterns, boundary overflows, type mismatches) to generate negative test cases.
    *   **Tooling**: Pure Logic (LLM Reasoning).

3.  **API Agent (The Executor)**:
    *   **Role**: Integration Tester.
    *   **Capabilities**: dynamic API interaction. Reads Postman collections to understand contracts, executes HTTP requests, and validates responses against expected status codes.
    *   **Tooling**: REST API MCP Server, Filesystem.

4.  **Excel Agent (The Reporter)**:
    *   **Role**: Data Analyst.
    *   **Capabilities**: Logs detailed test results, passes/failures, and payloads into structured formats (CSV/Excel) for human review.
    *   **Tooling**: Excel MCP Server, Filesystem.

## 🌟 Key Advantages & Learnings

### 1. Autonomous Reasoning
Traditional scripts fail when data changes. Our agents fetch the *current* table schema and adapt their payloads dynamically. If the "User" table gains a new "Age" column, the Database Agent sees it, and the Chaos Agent instantly starts testing its boundary conditions.

### 2. "Shift-Left" Security
By using a Chaos Agent to generate negative scenarios (fuzzing) automatically, we detect vulnerabilities (like unhandled 500 errors or security gaps) immediately during development, rather than weeks later.

### 3. Tool Interoperability (MCP)
We utilize the **Model Context Protocol (MCP)** to give agents standard interfaces to tools (SQL, Filesystem, HTTP). This modularity means we can swap the database (e.g., to PostgreSQL) or the reporter (e.g., to Jira) without rewriting the core agent logic.

### 4. Resilient Orchestration
Using a `RoundRobinGroupChat` with intelligent termination conditions allows the agents to converse until the task is truly done. If the API Agent fails a request, it can explain *why* to the Excel agent, ensuring the report contains context, not just generic errors.

---

## 🛠️ Usage Guide

### Prerequisites
*   **Python 3.11+**
*   **Docker** (for Database)
*   **Node.js & npm** (for MCP Servers)
*   `python-dotenv` (for security)

### Setup

1.  **Install Dependencies**:
    ```bash
    pip install autogen-agentchat autogen-ext[openai] python-dotenv
    ```
2.  **Configure Credentials**:
    Create a `.env` file in the root:
    ```env
    OPENAI_API_KEY=your_gemini_or_openai_key
    ```
3.  **Initialize Infrastructure**:
    Use our automated script to start the MySQL container and seed it with test data:
    ```bash
    python -m framework.setup_database
    ```

### Running Scenarios

#### 🟢 Scenario 1: User Registration (Happy Path)
End-to-end validation of the user sign-up flow.
```bash
python -m framework.scenario_user_registration
```
*   **Flow**: DB fetches sample -> API constructs payload -> API registers user -> Excel logs success.

#### 🔴 Scenario 2: Chaos Testing (Negative Path)
Stress-testing the API with invalid data.
```bash
python -m framework.scenario_chaos_test
```
*   **Flow**: DB fetches sample -> Chaos mutates data -> API attacks endpoint -> Excel logs vulnerabilities.
*   **Output**: Check `framework/resources/chaos_results.csv`.

---
*Built with ❤️ using AutoGen and Gemini Models.*
