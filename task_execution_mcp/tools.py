
import os
import subprocess
import requests
import json
import base64
from typing import Any, Dict, Optional

class ToolEngine:
    def __init__(self, base_dir: str = "/home/ubuntu/mcp_workspace"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def filesystem(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action") or kwargs.get("operation")
        path = kwargs.get("path") or kwargs.get("file_path") or kwargs.get("filename")
        content = kwargs.get("content") or kwargs.get("data") or kwargs.get("text")
        
        if not action or not path:
            return {"status": "error", "message": "Missing 'action' or 'path' for filesystem tool."}

        full_path = os.path.join(self.base_dir, path.lstrip("/"))
        try:
            if action == "write":
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write(content or "")
                return {"status": "success", "message": f"File written to {path}"}
            elif action == "read":
                if not os.path.exists(full_path):
                    return {"status": "error", "message": f"File not found: {path}"}
                with open(full_path, "r") as f:
                    return {"status": "success", "content": f.read()}
            elif action == "list":
                target = full_path if os.path.exists(full_path) and os.path.isdir(full_path) else os.path.dirname(full_path)
                return {"status": "success", "files": os.listdir(target)}
            else:
                return {"status": "error", "message": f"Unknown filesystem action: {action}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def http(self, **kwargs) -> Dict[str, Any]:
        method = kwargs.get("method", "GET")
        url = kwargs.get("url")
        headers = kwargs.get("headers")
        data = kwargs.get("data") or kwargs.get("body")
        
        if not url:
            return {"status": "error", "message": "Missing 'url' for http tool."}

        try:
            resp = requests.request(method, url, headers=headers, data=data, timeout=30)
            return {
                "status": "success",
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "body": resp.text
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def python(self, **kwargs) -> Dict[str, Any]:
        code = kwargs.get("code") or kwargs.get("script")
        if not code:
            return {"status": "error", "message": "Missing 'code' for python tool."}

        try:
            # Save to a temporary file and run
            script_path = os.path.join(self.base_dir, "_tmp_script.py")
            with open(script_path, "w") as f:
                f.write(code)
            
            result = subprocess.run(["python3", script_path], capture_output=True, text=True, timeout=60)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def process(self, **kwargs) -> Dict[str, Any]:
        command = kwargs.get("command") or kwargs.get("cmd")
        if not command:
            return {"status": "error", "message": "Missing 'command' for process tool."}

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60, cwd=self.base_dir)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def browser(self, action: str, url: str) -> Dict[str, Any]:
        # This is a simplified browser tool using requests for informational fetching
        # In a real scenario, this would interface with Playwright or Selenium
        if action == "fetch":
            return self.http("GET", url)
        else:
            return {"status": "error", "message": f"Browser action '{action}' not implemented in this minimal version."}

    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        method = getattr(self, tool_name, None)
        if method:
            return method(**kwargs)
        return {"status": "error", "message": f"Tool '{tool_name}' not found."}
