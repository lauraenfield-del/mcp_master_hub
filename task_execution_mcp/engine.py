
import json
from openai import OpenAI
from typing import List, Dict, Any
from tools import ToolEngine

class TaskEngine:
    def __init__(self, model: str = "gpt-5-mini"):
        self.client = OpenAI()
        self.model = model
        self.tools = ToolEngine()
        self.state = {}

    def _call_llm(self, system_prompt: str, user_prompt: str, response_format: Dict = None) -> str:
        params = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        if response_format:
            params["response_format"] = response_format
        
        resp = self.client.chat.completions.create(**params)
        return resp.choices[0].message.content

    def understand(self, task: str) -> Dict[str, Any]:
        system_prompt = "Classify the user's natural-language task and identify core needs. Output JSON."
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "understanding",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "classification": {"type": "string"},
                        "core_needs": {"type": "array", "items": {"type": "string"}},
                        "complexity": {"type": "string", "enum": ["low", "medium", "high"]}
                    },
                    "required": ["classification", "core_needs", "complexity"],
                    "additionalProperties": False
                }
            }
        }
        result = self._call_llm(system_prompt, task, response_format)
        self.state["task"] = task
        self.state["understanding"] = json.loads(result)
        return self.state["understanding"]

    def plan(self, understanding: Dict[str, Any]) -> List[str]:
        system_prompt = "Generate a tool-based execution plan (filesystem, http, python, process, browser). Output JSON list of steps."
        user_prompt = f"Task: {self.state.get('task')}\nUnderstanding: {json.dumps(understanding)}"
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "plan",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "steps": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["steps"],
                    "additionalProperties": False
                }
            }
        }
        result = self._call_llm(system_prompt, user_prompt, response_format)
        self.state["plan"] = json.loads(result)["steps"]
        return self.state["plan"]

    def execute(self, plan: List[str]) -> Dict[str, Any]:
        system_prompt = """Identify the next tool call needed for the plan.
Available Tools:
- filesystem(action: str, path: str, content: str = None) -> actions: write, read, list
- http(method: str, url: str, headers: dict = None, data: str = None)
- python(code: str)
- process(command: str)
- browser(action: str, url: str) -> actions: fetch

Output JSON with 'tool' and 'arguments'."""
        user_prompt = f"Plan: {json.dumps(plan)}\nHistory: {json.dumps(self.state.get('history', []))}\nCurrent State: {json.dumps(self.state)}"
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "tool_call",
                "strict": False,
                "schema": {
                    "type": "object",
                    "properties": {
                        "tool": {"type": "string", "enum": ["filesystem", "http", "python", "process", "browser"]},
                        "arguments": {"type": "object"}
                    },
                    "required": ["tool", "arguments"]
                }
            }
        }
        
        tool_spec = json.loads(self._call_llm(system_prompt, user_prompt, response_format))
        execution_result = self.tools.call_tool(tool_spec["tool"], **tool_spec["arguments"])
        
        # Record history
        if "history" not in self.state:
            self.state["history"] = []
        self.state["history"].append({"tool": tool_spec["tool"], "args": tool_spec["arguments"], "result": execution_result})
        
        self.state["last_execution"] = {"tool": tool_spec["tool"], "result": execution_result}
        return self.state["last_execution"]

    def review(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = "Verify if the execution result is correct or complete. Output JSON."
        user_prompt = f"Task: {self.state.get('task')}\nResult: {json.dumps(execution_result)}"
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "review",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "is_complete": {"type": "boolean"},
                        "feedback": {"type": "string"},
                        "suggested_fix": {"type": "string", "nullable": True}
                    },
                    "required": ["is_complete", "feedback", "suggested_fix"],
                    "additionalProperties": False
                }
            }
        }
        result = self._call_llm(system_prompt, user_prompt, response_format)
        self.state["review"] = json.loads(result)
        return self.state["review"]

    def fix(self, review_feedback: Dict[str, Any]) -> Dict[str, Any]:
        if review_feedback["is_complete"]:
            return {"status": "no_fix_needed", "message": "Task is already complete."}
        
        system_prompt = """Generate a fix action based on review feedback.
Available Tools:
- filesystem(action: str, path: str, content: str = None)
- http(method: str, url: str, headers: dict = None, data: str = None)
- python(code: str)
- process(command: str)
- browser(action: str, url: str)

Output JSON with 'tool' and 'arguments'."""
        user_prompt = f"Feedback: {json.dumps(review_feedback)}\nState: {json.dumps(self.state)}"
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "fix_action",
                "strict": False,
                "schema": {
                    "type": "object",
                    "properties": {
                        "tool": {"type": "string", "enum": ["filesystem", "http", "python", "process", "browser"]},
                        "arguments": {"type": "object"}
                    },
                    "required": ["tool", "arguments"]
                }
            }
        }
        tool_spec = json.loads(self._call_llm(system_prompt, user_prompt, response_format))
        fix_result = self.tools.call_tool(tool_spec["tool"], **tool_spec["arguments"])
        
        if "history" not in self.state:
            self.state["history"] = []
        self.state["history"].append({"type": "fix", "tool": tool_spec["tool"], "args": tool_spec["arguments"], "result": fix_result})
        
        self.state["last_fix"] = {"tool": tool_spec["tool"], "result": fix_result}
        return self.state["last_fix"]

    def complete(self) -> Dict[str, Any]:
        system_prompt = "Summarize the final result of the task. Output JSON."
        user_prompt = f"Task: {self.state.get('task')}\nHistory: {json.dumps(self.state)}"
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "final_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "artifacts": {"type": "array", "items": {"type": "string"}},
                        "status": {"type": "string"}
                    },
                    "required": ["summary", "artifacts", "status"],
                    "additionalProperties": False
                }
            }
        }
        result = self._call_llm(system_prompt, user_prompt, response_format)
        return json.loads(result)
