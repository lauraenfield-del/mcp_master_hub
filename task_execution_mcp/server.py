
from flask import Flask, request, jsonify
from engine import TaskEngine
import os

app = Flask(__name__)
engine = TaskEngine()

@app.route('/input_step', methods=['POST'])
def input_step():
    user_request = request.json.get('text_input', '')
    engine.state = {"task": user_request}
    return jsonify({"status": "success", "message": "Task initialized.", "request": user_request})

@app.route('/understand_step', methods=['POST'])
def understand_step():
    task = engine.state.get("task", "")
    if not task:
        return jsonify({"status": "error", "message": "No task initialized. Call /input_step first."}), 400
    understanding = engine.understand(task)
    return jsonify({"status": "success", "message": "Task classified.", "understanding": understanding})

@app.route('/plan_step', methods=['POST'])
def plan_step():
    understanding = engine.state.get("understanding")
    if not understanding:
        return jsonify({"status": "error", "message": "No understanding found. Call /understand_step first."}), 400
    plan = engine.plan(understanding)
    return jsonify({"status": "success", "message": "Execution plan generated.", "plan": plan})

@app.route('/execute_step', methods=['POST'])
def execute_step():
    plan = engine.state.get("plan")
    if not plan:
        return jsonify({"status": "error", "message": "No plan found. Call /plan_step first."}), 400
    result = engine.execute(plan)
    return jsonify({"status": "success", "message": "Tool execution complete.", "execution_result": result})

@app.route('/review_step', methods=['POST'])
def review_step():
    last_exec = engine.state.get("last_execution")
    if not last_exec:
        return jsonify({"status": "error", "message": "No execution result to review. Call /execute_step first."}), 400
    review = engine.review(last_exec)
    return jsonify({"status": "success", "message": "Review complete.", "review_feedback": review})

@app.route('/fix_step', methods=['POST'])
def fix_step():
    review = engine.state.get("review")
    if not review:
        return jsonify({"status": "error", "message": "No review feedback found. Call /review_step first."}), 400
    fix_result = engine.fix(review)
    return jsonify({"status": "success", "message": "Fix applied.", "fix_result": fix_result})

@app.route('/complete_step', methods=['POST'])
def complete_step():
    if not engine.state.get("task"):
        return jsonify({"status": "error", "message": "No task found."}), 400
    final_result = engine.complete()
    return jsonify({"status": "success", "message": "Task loop complete.", "final_result": final_result})

if __name__ == '__main__':
    # Ensure workspace exists
    os.makedirs("/home/ubuntu/mcp_workspace", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
