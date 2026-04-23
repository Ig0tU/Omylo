import os
import json
from typing import Dict, Any, Optional

class MetricsManager:
    """
    Manages global metrics and budget tracking.
    """
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.metrics_file = os.path.join(self.root_dir, ".mythos_metrics.json")
        self.metrics = self.load_metrics()

    def load_metrics(self) -> Dict[str, Any]:
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"total_tokens": 0, "total_cost": 0.0, "sessions": 0}

    def save_metrics(self):
        with open(self.metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)

    def update_metrics(self, tokens: int, cost: float):
        self.metrics["total_tokens"] += tokens
        self.metrics["total_cost"] += cost
        self.metrics["sessions"] += 1
        self.save_metrics()

    def get_stats(self) -> Dict[str, Any]:
        return self.metrics
