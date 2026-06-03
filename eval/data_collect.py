import time
import json
from typing import Dict, Any, List, Tuple
import asyncio
from typefly.llm_controller import LLMController
from typefly.llm_planner import LLMPlanner
from typefly.robot_wrapper import RobotWrapper
from typefly.yolo_client import YoloClient
class DroneDataCollector:
    def __init__(self, llm_planner: LLMPlanner, robot_wrapper: RobotWrapper, yolo_client: YoloClient,llm_controller: LLMController):
        self.llm_planner = llm_planner
        self.robot_wrapper = robot_wrapper
        self.yolo_client = yolo_client
        self.collect_data: List[Dict[str, Any]] = []
        self.controller = llm_controller
    # 采集LLM规划数据
    def collect_llm_data(self, instruction: str) -> Dict[str, Any]:
        start_time = time.time()
        plan = self.llm_planner.plan(instruction)  # 调用TypeFly的LLM规划接口
        planning_time = time.time() - start_time
        return {
            "timestamp": time.time(),
            "type": "llm_planning",
            "instruction": instruction,
            "planning_result": plan,
            "planning_time": planning_time,
            "is_understood": plan is not None
        }
    # 采集无人机执行数据
    def collect_robot_execution_data(self, planned:str) -> Dict[str, Any]:
        start_time = time.time()
        exceptions = False
        path_deviations =0.0
        try:
            planned_pose=tuple(self.robot_wrapper.obs.position)
            pose_str = self.controller.planner.probe(
                f"这是无人机的飞行计划：<{planned}>\n"
                f"这是无人机当前位置：x={planned_pose[0]}, y={planned_pose[1]}, z={planned_pose[2]}\n"
                f"请严格按照格式输出最终预测坐标，仅返回数字，格式为：x,y,z",self.robot_wrapper.robot_info
            )
            planned_pose=tuple([float(x) for x in pose_str.split(',')])
            print(planned_pose)
            if len(planned_pose)!=3:
                planned_pose = tuple(self.robot_wrapper.obs.position)
            self.controller.work(planned)
            actual_pose= tuple(self.robot_wrapper.obs.position)
            # 计算位姿偏差（欧氏距离）
            path_deviations = self._calculate_pose_deviation(planned_pose, actual_pose)
        except Exception as e:
            exceptions = True
            print(e)

        run_time = time.time() - start_time
        return {
            "timestamp": time.time(),
            "type": "robot_execution",
            "planned_actions": planned,
            "total_run_time": run_time,
            "avg_path_deviation": path_deviations ,
            "has_exception": exceptions
        }

    # 采集视觉识别数据
    def collect_vision_data(self, target_objects: list) -> Dict[str, Any]:
        frame = self.robot_wrapper.obs.image # 获取无人机摄像头帧
        detection_result = asyncio.run(self.yolo_client.detect(frame)) or [] # 调用YOLO检测接口
        # 统计识别结果
        recognized_targets = [obj for obj in detection_result if obj["name"] in target_objects]
        actual_target_count = len(target_objects)
        recognized_count = len(recognized_targets)

        # 计算目标定位误差（与真实位姿对比）
        location = []
        for target in target_objects:
            detected_pose = next((obj["pose"] for obj in detection_result if obj["name"] == target), None)
            location.append(detected_pose)

        return {
            "timestamp": time.time(),
            "type": "vision_detection",
            "detection_result": detection_result,
            "actual_target_count": actual_target_count,
            "recognized_count": recognized_count,
            "location": location if location else [0.0]
        }
    # 辅助：计算欧氏距离
    def _calculate_pose_deviation(self, pose1: Tuple[float, float, float], pose2: Tuple[float, float, float]) -> float:
        return ((pose1[0] - pose2[0]) ** 2 + (pose1[1] - pose2[1]) ** 2 + (pose1[2] - pose2[2]) ** 2) ** 0.5
    # 保存采集数据
    def save_data(self, save_path: str):
        with open(save_path, "w") as f:
            json.dump(self.collect_data, f, indent=4)
    # 重置采集数据
    def reset(self):
        self.collect_data = []