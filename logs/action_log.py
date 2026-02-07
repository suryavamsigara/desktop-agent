import json
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "action_log.json")

class ActionLog:
    def __init__(self, path=LOG_PATH, goal=""):
        self.path = path
        self.goal = goal
        self._load_or_init()
        self._start_new_run()
    
    def _load_or_init(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    self.store = {"runs": []}
                else:
                    self.store = json.loads(content)
        else:
            self.store = {"runs": []}
    
    def _start_new_run(self):
        self.run_id = len(self.store["runs"]) + 1
        self.run = {
            "run_id": self.run_id,
            "goal": self.goal,
            "started_at": time.time(),
            "ended_at": None,
            "actions": []
        }
        self.store["runs"].append(self.run)
        self._save()

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.store, f, indent=2, ensure_ascii=False)
    
    def log_tool(self, name, tool_input, tool_output):
        self.run["actions"].append({
            "ts": time.time(),
            "type": "tool",
            "name": name,
            "input": tool_input,
            "output": tool_output
        })
        self._save()

    def log_final(self, text):
        self.run["actions"].append({
            "ts": time.time(),
            "type": "final",
            "output": text
        })
        self.run["ended_at"] = time.time()
        self._save()
