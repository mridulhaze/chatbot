"""
National University AI Lab — State & Task Persistence Manager
Maintains lab_state.json, task queues, cycle counters, and metrics.
"""

import os
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("NU_AI_LAB_STATE")

LAB_DIR = Path("E:/projects/AI_CHAT_BOT/ai_lab")
STATE_FILE = LAB_DIR / "lab_state.json"

# Ensure all workspace directories exist
for sub in [
    "research", "qa_reports", "tasks", "implementations",
    "test_results", "regressions", "research_sources",
    "cycle_reports", "metrics"
]:
    (LAB_DIR / sub).mkdir(parents=True, exist_ok=True)

DEFAULT_STATE: Dict[str, Any] = {
    "autonomous_mode": "STOPPED",  # "STOPPED", "RUNNING", "PAUSED"
    "current_cycle": 0,
    "current_task": None,
    "agent1_status": "IDLE",
    "agent1_activity": "Waiting for start signal",
    "agent2_status": "IDLE",
    "agent2_activity": "Waiting for QA tasks",
    "open_critical": 0,
    "open_high": 0,
    "open_medium": 0,
    "open_low": 0,
    "total_resolved": 0,
    "total_regressions": 0,
    "average_accuracy": 9.4,
    "average_context": 9.2,
    "average_relevance": 9.5,
    "average_overall_score": 9.35,
    "last_cycle_timestamp": None,
    "next_cycle_timestamp": None,
    "cooldown_seconds": 120,
    "max_tests_per_cycle": 12,
    "quality_gate": {
        "min_accuracy": 9.0,
        "min_relevance": 9.0,
        "min_context": 8.5,
        "min_safety": 9.5,
        "min_overall": 9.0,
        "max_critical_allowed": 0,
        "max_high_allowed": 0
    },
    "history_metrics": []
}

class LabStateManager:
    def __init__(self):
        self.state_file = STATE_FILE
        self._load_state()

    def _load_state(self):
        if not self.state_file.exists():
            self.state = DEFAULT_STATE.copy()
            self._save_state()
        else:
            try:
                self.state = json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Failed to load {self.state_file}, initializing default: {e}")
                self.state = DEFAULT_STATE.copy()
                self._save_state()

    def _save_state(self):
        try:
            self.state_file.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to write state: {e}")

    def get_state(self) -> Dict[str, Any]:
        self._load_state()
        return self.state

    def set_mode(self, mode: str):
        valid = ["STOPPED", "RUNNING", "PAUSED"]
        if mode in valid:
            self.state["autonomous_mode"] = mode
            if mode == "STOPPED":
                self.state["agent1_status"] = "STOPPED"
                self.state["agent1_activity"] = "System stopped by operator"
                self.state["agent2_status"] = "STOPPED"
                self.state["agent2_activity"] = "System stopped by operator"
            elif mode == "PAUSED":
                self.state["agent1_status"] = "PAUSED"
                self.state["agent1_activity"] = "Cycle paused safely"
                self.state["agent2_status"] = "PAUSED"
                self.state["agent2_activity"] = "Cycle paused safely"
            elif mode == "RUNNING":
                self.state["agent1_status"] = "ACTIVE"
                self.state["agent1_activity"] = "Ready for execution"
                self.state["agent2_status"] = "ACTIVE"
                self.state["agent2_activity"] = "Ready for tasks"
            self._save_state()

    def update_agent1(self, status: str, activity: str):
        self.state["agent1_status"] = status
        self.state["agent1_activity"] = activity
        self._save_state()

    def update_agent2(self, status: str, activity: str):
        self.state["agent2_status"] = status
        self.state["agent2_activity"] = activity
        self._save_state()

    def increment_cycle(self) -> int:
        self.state["current_cycle"] = self.state.get("current_cycle", 0) + 1
        self.state["last_cycle_timestamp"] = datetime.now(timezone.utc).isoformat()
        self._save_state()
        return self.state["current_cycle"]

    def update_scores(self, accuracy: float, context: float, relevance: float, overall: float):
        self.state["average_accuracy"] = round(accuracy, 2)
        self.state["average_context"] = round(context, 2)
        self.state["average_relevance"] = round(relevance, 2)
        self.state["average_overall_score"] = round(overall, 2)
        
        # Append to metrics history (keep last 50)
        history = self.state.get("history_metrics", [])
        history.append({
            "cycle": self.state["current_cycle"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "accuracy": round(accuracy, 2),
            "context": round(context, 2),
            "relevance": round(relevance, 2),
            "overall": round(overall, 2)
        })
        self.state["history_metrics"] = history[-50:]
        self._save_state()

    def update_issue_counts(self, critical: int, high: int, medium: int, low: int, resolved: int, regressions: int):
        self.state["open_critical"] = critical
        self.state["open_high"] = high
        self.state["open_medium"] = medium
        self.state["open_low"] = low
        self.state["total_resolved"] = self.state.get("total_resolved", 0) + resolved
        self.state["total_regressions"] = self.state.get("total_regressions", 0) + regressions
        self._save_state()

    def save_task(self, task: Dict[str, Any]):
        task_id = task.get("task_id", f"TASK-{int(time.time())}")
        task_path = LAB_DIR / "tasks" / f"{task_id}.json"
        task_path.write_text(json.dumps(task, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        tasks = []
        for p in (LAB_DIR / "tasks").glob("*.json"):
            try:
                tasks.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                pass
        return sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)

_instance = None
def get_lab_state() -> LabStateManager:
    global _instance
    if _instance is None:
        _instance = LabStateManager()
    return _instance
