# Framework Module

This folder contains the core components of the agentic framework.

## Components

*   **`agentFactory.py`**: Factory class to create specialized agents (Database, API, Excel, Chaos).
*   **`mcp_config.py`**: Configuration for Model Context Protocol (MCP) servers (MySQL, Filesystem, Rest API, Excel).

## Scenarios

*   **`scenario_user_registration.py`**: Former `scenario2.py`. Orchestrates a complete happy-path registration flow.
*   **`scenario_chaos_test.py`**: Former `scenario_chaos.py`. Orchestrates a fuzz-testing flow involving Chaos Agent.

## Usage

Run scenarios as modules:
```bash
python -m framework.scenario_chaos_test
```
