import json
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "action_log.json")

class ActionLog:
    def __init__(self, path=LOG_PATH, goal=""):
        self.path = path
        self.data = {
            "goal": goal,
            "started_at": time.time(),
            "ended_at": None,
            "actions": []
        }
        self._save()
    
    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def log_tool(self, name, tool_input, tool_output):
        self.data["actions"].append({
            "ts": time.time(),
            "type": "tool",
            "name": name,
            "input": tool_input,
            "output": tool_output
        })
        self._save()

    def log_final(self, text):
        self.data["actions"].append({
            "ts": time.time(),
            "type": "final",
            "output": text
        })
        self.data["ended_at"] = time.time()
        self._save()
