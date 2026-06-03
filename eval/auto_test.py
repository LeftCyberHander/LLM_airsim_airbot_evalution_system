# auto_tester.py
import time
from typing import List, Dict

import json

from typefly.eval.scenario import DroneTaskScenario, get_default_scenarios
from typefly.eval.data_collect import DroneDataCollector
from typefly.eval.test import DroneEvaluationMetrics
from typefly.llm_controller import LLMController
from typefly.llm_planner import LLMPlanner
from typefly.robot_wrapper import RobotWrapper
from typefly.yolo_client import YoloClient
from typefly.eval.report_gen import generate_evaluation_report


class DroneAutoTester:
    def __init__(self, llm_planner: LLMPlanner, robot_wrapper: RobotWrapper, yolo_client: YoloClient,llm_controller: LLMController):
        self.data_collector = DroneDataCollector(llm_planner, robot_wrapper, yolo_client,llm_controller)
        self.metrics_calculator = DroneEvaluationMetrics()
        self.test_results = {}
    def run_single_scenario(self, scenario: DroneTaskScenario) -> Dict:
        print(f"开始执行场景测试: {scenario.scenario_id} - {scenario.task_description}")
        self.data_collector.reset()
        self.metrics_calculator.reset()
        # 1. 初始化无人机
        self.data_collector.robot_wrapper.set_position(*scenario.drone_init_pose)
        time.sleep(1)
        # 2. 采集LLM规划数据
        llm_data = self.data_collector.collect_llm_data(scenario.task_description)
        self.data_collector.collect_data.append(llm_data)
        self.metrics_calculator.update_llm_planning(llm_data["planning_time"], llm_data["is_understood"])
        # 3. 采集视觉数据
        vision_data =  self.data_collector.collect_vision_data(scenario.target_objects)
        self.data_collector.collect_data.append(vision_data)
        self.metrics_calculator.update_vision_accuracy(
            vision_data["actual_target_count"],
            vision_data["recognized_count"],
            vision_data["location"][0] if vision_data["location"] else 0.0
        )

        # 4. 执行任务并采集执行数据
        if llm_data["is_understood"]:
            #print((llm_data["planning_result"]))
            try:
                got_plan= json.loads(llm_data["planning_result"])
            #print(got_plan["plan"])
                execution_data = self.data_collector.collect_robot_execution_data(got_plan["plan"])
                self.data_collector.collect_data.append(execution_data)
                self.metrics_calculator.update_execution_stability(
                    execution_data["avg_path_deviation"],
                    execution_data["has_exception"],
                    execution_data["total_run_time"]
                )
                is_task_completed = not execution_data["has_exception"]
            except json.JSONDecodeError:
                is_task_completed = False
        else:
            is_task_completed = False

        # 5. 更新任务完成度
        self.metrics_calculator.update_task_completion(is_task_completed)

        # 6. 计算该场景的评测结果
        scenario_metrics = self.metrics_calculator.calculate_metrics()
        self.test_results[scenario.scenario_id] = {
            "scenario_info": scenario.__dict__,
            "raw_data": self.data_collector.collect_data,
            "metrics": scenario_metrics,
            "is_completed": is_task_completed
        }

        print(f"场景测试完成: {scenario.scenario_id} - 任务完成状态: {is_task_completed}")
        return self.test_results[scenario.scenario_id]

    # 批量执行场景测试
    def run_batch_scenarios(self, scenarios: List[DroneTaskScenario], report_save_path: str = "evaluation_report.html"):
        for scenario in scenarios:
             self.run_single_scenario(scenario)

        # 生成综合评测报告
        generate_evaluation_report(self.test_results, report_save_path)
        print(f"批量测试完成，评测报告已保存至: {report_save_path}")