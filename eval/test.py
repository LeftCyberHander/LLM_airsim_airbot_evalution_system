import time
import numpy as np
from typing import Dict, List, Tuple
class DroneEvaluationMetrics:
    def __init__(self):# 初始化
        self.metrics_data = \
        {
            "task_completion": {"total": 0, "completed": 0},
            "llm_planning": {"total_time": 0.0, "count": 0, "correct_understanding": 0, "total_instructions": 0},
            "vision_accuracy": {"total_targets": 0, "correct_recognized": 0, "location": []},
            "execution_stability": {"path_deviations": [], "exceptions": 0, "total_running_time": 0.0}
        }
    def update_task_completion(self, is_completed: bool):# 1. 任务完成度
        self.metrics_data["task_completion"]["total"] += 1
        if is_completed:
            self.metrics_data["task_completion"]["completed"] += 1
    def update_llm_planning(self, planning_time: float, is_understood: bool):# 2. LLM规划
        self.metrics_data["llm_planning"]["total_time"] += planning_time
        self.metrics_data["llm_planning"]["count"] += 1
        self.metrics_data["llm_planning"]["total_instructions"] += 1
        if is_understood:
            self.metrics_data["llm_planning"]["correct_understanding"] += 1
    def update_vision_accuracy(self, actual_targets: int, recognized_targets: int, location: float):# 3. 视觉感知
        self.metrics_data["vision_accuracy"]["total_targets"] += actual_targets
        self.metrics_data["vision_accuracy"]["correct_recognized"] += recognized_targets
        self.metrics_data["vision_accuracy"]["location"].append(location)
    def update_execution_stability(self, path_deviation: float, has_exception: bool, run_time: float):# 4. 执行稳定性
        self.metrics_data["execution_stability"]["path_deviations"].append(path_deviation)
        if has_exception:
            self.metrics_data["execution_stability"]["exceptions"] += 1
        self.metrics_data["execution_stability"]["total_running_time"] += run_time
    # 计算all
    def calculate_metrics(self) -> Dict:
        results = {}
        # 1
        total_tasks = self.metrics_data["task_completion"]["total"]
        results["task_completion_rate"] = (self.metrics_data["task_completion"][ "completed"] / total_tasks) * 100 if total_tasks > 0 else 0.0
        # 2
        llm_count = self.metrics_data["llm_planning"]["count"]
        results["avg_planning_time"] = self.metrics_data["llm_planning"]["total_time"] / llm_count if llm_count > 0 else 0.0
        total_instr = self.metrics_data["llm_planning"]["total_instructions"]
        results["llm_understanding_accuracy"] = (self.metrics_data["llm_planning"][ "correct_understanding"] / total_instr) * 100 if total_instr > 0 else 0.0
        # 3
        total_targets = self.metrics_data["vision_accuracy"]["total_targets"]
        results["vision_recognition_accuracy"] = (self.metrics_data["vision_accuracy"][ "correct_recognized"] / total_targets) * 100 if total_targets > 0 else 0.0
        loc = self.metrics_data["vision_accuracy"]["location"]
        results["location"] = loc if loc else 0.0
        # 4
        path_devs = self.metrics_data["execution_stability"]["path_deviations"]
        results["avg_path_deviation"] = np.mean(path_devs) if path_devs else 0.0
        total_run_time = self.metrics_data["execution_stability"]["total_running_time"]
        results["exception_rate"] = self.metrics_data["execution_stability"][ "exceptions"] / total_run_time if total_run_time > 0 else 0.0

        return results
    def reset(self):
        self.__init__()