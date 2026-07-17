# Task Execution MCP Engine

A fully functional, universal task-execution engine implementing the Model Context Protocol (MCP). This server transforms natural-language instructions into real actions through an LLM-powered 7-step loop and a robust system toolset.

## Key Features

-   **LLM-Powered Logic**: Each step (Understand, Plan, Review, Fix, Complete) is driven by an LLM (default: `gpt-5-mini`) for intelligent decision-making.
-   **Universal Toolset**: Built-in routing for:
    -   `filesystem`: Read, write, and list files in a dedicated workspace.
    -   `http`: Perform web requests (GET, POST, etc.).
    -   `python`: Execute arbitrary Python code in the local environment.
    -   `process`: Run shell commands and interact with the system.
    -   `browser`: Simplified informational web fetching.
-   **Structured Execution**: Follows a strict task loop to ensure reliability and correctness.
-   **Plug-and-Play**: Designed for immediate integration with LM Studio, CrewAI, and other MCP-compatible clients.

## The Task Execution Loop

1.  **INPUT**: Receives the natural-language task.
2.  **UNDERSTAND**: Classifies the task and identifies core needs.
3.  **PLAN**: Generates a step-by-step tool-based execution plan.
4.  **EXECUTE**: Routes to the appropriate tool to perform real actions.
5.  **REVIEW**: Evaluates the output against the original task.
6.  **FIX**: Retries or adjusts execution if the review fails.
7.  **DONE**: Returns a structured summary and list of artifacts.

## Setup and Installation

### Prerequisites

-   Python 3.10+
-   `OPENAI_API_KEY` environment variable set (for the engine logic).

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/lauraenfield-del/mcp_master_hub.git
    cd mcp_master_hub/task_execution_mcp
    ```

2.  **Install dependencies**:
    ```bash
    pip install flask requests openai
    ```

3.  **Run the server**:
    ```bash
    python server.py
    ```
    The server starts on `http://0.0.0.0:5000`.

## API Usage

The server exposes endpoints corresponding to the task loop steps. Each endpoint accepts a `POST` request with a JSON body: `{"text_input": "..."}`.

| Endpoint | Description |
| :--- | :--- |
| `/input_step` | Initialize a new task. |
| `/understand_step` | Classify and analyze the task. |
| `/plan_step` | Generate a tool-based plan. |
| `/execute_step` | Execute the next tool call in the plan. |
| `/review_step` | Review the execution result. |
| `/fix_step` | Apply fixes if needed. |
| `/complete_step` | Get the final task summary. |

## Workspace

All filesystem operations are restricted to `/home/ubuntu/mcp_workspace` to ensure safety and organization.

## Customization

You can modify `engine.py` to change the underlying LLM model or add new tools to `tools.py`. The `manifest.json` provides the standard interface for MCP clients.
