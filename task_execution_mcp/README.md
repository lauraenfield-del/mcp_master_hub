# Task Execution MCP Server

This Model Context Protocol (MCP) server provides a generic, reusable framework for executing tasks through a 7-step loop. It is designed to be plug-and-play for systems like LM Studio or CrewAI, offering a structured approach to task automation without project-specific logic.

## Task Execution Loop

The server implements the following sequential steps for any given task:

1.  **INPUT**: Receives the initial user request.
2.  **UNDERSTAND**: Interprets the request to identify core needs and objectives.
3.  **PLAN**: Generates a clear, step-by-step plan to address the interpreted request.
4.  **EXECUTE**: Performs the planned steps using available MCP tools or internal logic.
5.  **REVIEW**: Evaluates the results of the execution for correctness and completeness.
6.  **FIX**: Adjusts or retries steps if the review indicates deficiencies.
7.  **DONE**: Returns the final, validated result to the user.

## Exposed MCP Actions

The server exposes the following MCP actions, each accepting text input and returning structured JSON:

-   `input_step`: Receives the user's initial request.
    -   **Input**: `{"text_input": "<user_request_string>"}`
    -   **Output**: `{"status": "success", "message": "User request received.", "request": "<user_request_string>"}`

-   `understand_step`: Interprets the received request.
    -   **Input**: `{"text_input": "<request_to_understand_string>"}`
    -   **Output**: `{"status": "success", "message": "Request understood.", "understanding": "<interpreted_request_string>"}`

-   `plan_step`: Generates a plan based on the understanding.
    -   **Input**: `{"text_input": "<understanding_string>"}`
    -   **Output**: `{"status": "success", "message": "Plan generated.", "plan": ["<step_1>", "<step_2>", ...]}`

-   `execute_step`: Executes the generated plan.
    -   **Input**: `{"text_input": "<plan_or_step_to_execute_string>"}`
    -   **Output**: `{"status": "success", "message": "Execution complete.", "execution_result": "<execution_summary_string>"}`

-   `review_step`: Reviews the execution result.
    -   **Input**: `{"text_input": "<execution_result_string>"}`
    -   **Output**: `{"status": "success", "message": "Review complete.", "review_feedback": "<review_feedback_string>"}`

-   `fix_step`: Applies fixes or adjustments based on review feedback.
    -   **Input**: `{"text_input": "<review_feedback_string>"}`
    -   **Output**: `{"status": "success", "message": "Fix applied.", "fix_action": "<fix_action_description_string>"}`

-   `complete_step`: Returns the final result of the task.
    -   **Input**: `{"text_input": "<final_result_string>"}`
    -   **Output**: `{"status": "success", "message": "Task completed.", "final_result": "<final_result_string>"}`

## Setup and Usage

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/lauraenfield-del/mcp_master_hub.git
    cd mcp_master_hub/task_execution_mcp
    ```

2.  **Install dependencies** (if using Python):
    ```bash
    pip install Flask
    ```

3.  **Run the server**:
    ```bash
    python server.py
    ```
    The server will run on `http://0.0.0.0:5000`.

4.  **Interact with the MCP actions** using HTTP POST requests to the respective endpoints (e.g., `http://localhost:5000/input_step`).

## Customization

This server is designed to be a generic template. To make it functional for specific tasks, you will need to replace the `<PLACEHOLDER_LOGIC_...>` comments in `server.py` with actual implementation logic that integrates with your tools and models. The `manifest.json` defines the interface, and `server.py` provides the basic Flask application structure.
