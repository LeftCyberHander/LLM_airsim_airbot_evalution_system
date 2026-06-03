import time
from typing import Any
from overrides import overrides
import airsim
import numpy as np
from PIL import Image
import threading

import random

from ..robot_wrapper import RobotWrapper, RobotObservation
from ..yolo_client import YoloClient
from ..robot_info import RobotInfo

import logging

logging.getLogger("airsim").setLevel(logging.WARNING)

MOVEMENT_MIN = 0.1  # 米
MOVEMENT_MAX = 10.0  # 米

ROTATION_MIN = 1.0  # 度
ROTATION_MAX = 360.0  # 度

EXECUTION_DELAY = 1  # 秒
VELOCITY = 1.0  # 米/秒

_thread_local=threading.local()
class AirSimWrapper(RobotWrapper):
    robot_list=[]
    def __init__(self, robot_info: RobotInfo):
        # 无人机配置
        self.vehicle_name = ""  # 默认无人机
        if "vehicle_name" in robot_info.extra:
            self.vehicle_name = robot_info.extra["vehicle_name"]
        AirSimWrapper.robot_list.append(self.vehicle_name)
        super().__init__(robot_info, AirSimObservation(self, robot_info))

        # 额外技能
        self.skillset.add_skill(self.takeoff, "Take off to specified altitude")
        self.skillset.add_skill(self.land, "Land the drone")
        self.skillset.add_skill(self.lift, "Move up/down by a distance")
        self.skillset.add_skill(self.set_position, "Fly to absolute position (NED)")

        # 状态跟踪
        self.running = True
        self.altitude = 0.0
    level_list = ["Stylized_Nature_ExampleScene", "RuralAustralia_Example_01", "Desert_A", "Demo_Namhansanseong",
                  "Map_one"]
    def set_name(self,name: str):
        self.vehicle_name=name
    def get_drone(self):
        """获取当前线程专属的 AirSim 客户端，自动完成连接和初始化"""
        if not hasattr(_thread_local, 'drone'):
            # 首次在当前线程使用时创建客户端
            drone = airsim.MultirotorClient()
            drone.confirmConnection()
            drone.enableApiControl(True, self.vehicle_name)
            drone.armDisarm(True, self.vehicle_name)
            _thread_local.drone = drone
        return _thread_local.drone
    def change_level(self, level_name):
        client=self.get_drone()
        self.obs.stop()
        client.simLoadLevel(level_name)

        self.obs.restart()
    def create_drone(self, drone_id, drone_type):
        client=self.get_drone()
        drone_id = "ccssxxoffly" + drone_id
        type = "simpleflight"
        pose = airsim.Pose(position_val=airsim.Vector3r(random.randint(1,5), random.randint(1,5), random.randint(1,5)-5),
                           orientation_val=airsim.to_quaternion(0, 0, 0))
        AirSimWrapper.robot_list.append(drone_id)
        if drone_type == 4:
            return client.simAddVehicle(str(drone_id), type, pose)
        else:
            return client.simAddVehicle(str(drone_id), type, pose, "Hexrotor")

    def _cap_dist(self, dist):
        """限制移动距离"""
        if abs(dist) < MOVEMENT_MIN:
            return MOVEMENT_MIN if dist >= 0 else -MOVEMENT_MIN
        elif abs(dist) > MOVEMENT_MAX:
            return MOVEMENT_MAX if dist >= 0 else -MOVEMENT_MAX
        return dist

    def _cap_angle(self, angle):
        """限制旋转角度"""
        if abs(angle) < ROTATION_MIN:
            return ROTATION_MIN if angle >= 0 else -ROTATION_MIN
        elif abs(angle) > ROTATION_MAX:
            return ROTATION_MAX if angle >= 0 else -ROTATION_MAX
        return angle

    @overrides
    def start(self) -> bool:
        """启动无人机"""
        print("-> AirSim drone connected")
        self.obs.start()
        return True

    @overrides
    def stop(self) -> bool:
        """停止并降落无人机"""
        print("-> Landing AirSim drone")
        self.land()
        drone = self.get_drone()
        drone.armDisarm(False, self.vehicle_name)
        drone.enableApiControl(False, self.vehicle_name)
        self.obs.stop()
        self.running = False
        return True

    def is_taken_off(self) -> bool:
        try:
            state = self.get_drone().getMultirotorState(self.vehicle_name)
            return state.landed_state ==2
        except Exception as e:
            print(f"-> 获取状态失败: {e}")
            return False
    def takeoff(self, altitude: float = 5.0):
        if self.is_taken_off():
            self.get_drone().moveToZAsync(
                altitude,  # 目标高度
                VELOCITY,  # 飞行速度
                self.vehicle_name
            ).join()
        else:
            self.get_drone().takeoffAsync(altitude, self.vehicle_name).join()

        # 统一更新高度 + 延迟
        self.altitude = altitude
        time.sleep(EXECUTION_DELAY)

    def land(self):
        """降落（重复调用不卡死）"""
        if not self.is_taken_off():
            print("-> 已在地面，无需降落")
            return

        print("-> 正在降落")
        self.get_drone().landAsync(self.vehicle_name).join()
        self.altitude = 0.0
        time.sleep(EXECUTION_DELAY)

    @overrides
    def _move(self, dx: float, dy: float):
        """相对移动（机体坐标系）"""
        print(f"-> Move by ({dx}, {dy}) m")

        dx = self._cap_dist(dx)
        dy = self._cap_dist(dy)

        # 计算移动时间
        dist = np.sqrt(dx ** 2 + dy ** 2)
        duration = dist / VELOCITY

        # 在机体坐标系中移动
        self.get_drone().moveByVelocityBodyFrameAsync(
            dx / duration,  # 前向速度
            dy / duration,  # 侧向速度
            0,  # 垂直速度
            duration,
            drivetrain=airsim.DrivetrainType.MaxDegreeOfFreedom,
            yaw_mode=airsim.YawMode(False, 0),
            vehicle_name=self.vehicle_name
        ).join()

        time.sleep(EXECUTION_DELAY)

    @overrides
    def _rotate(self, deg: float):
        """旋转"""
        print(f"-> Rotate by {deg} degrees")

        deg = self._cap_angle(deg)

        # 获取当前偏航角
        state = self.get_drone().getMultirotorState(self.vehicle_name)
        orientation = state.kinematics_estimated.orientation
        current_yaw = airsim.to_eularian_angles(orientation)[2]

        # 计算目标偏航角
        target_yaw = current_yaw + np.deg2rad(deg)

        # 旋转到目标偏航角
        self.get_drone().rotateToYawAsync(
            np.rad2deg(target_yaw),
            margin=1.0,
            vehicle_name=self.vehicle_name
        ).join()

        time.sleep(EXECUTION_DELAY)

    def lift(self, dist: float):
        """垂直升降"""
        print(f"-> Lift for {dist} m")

        dist = self._cap_dist(dist)

        if dist > 0:
            # 上升
            self.get_drone().moveToZAsync(
                -self.altitude - dist,  # AirSim中Z向下为负
                VELOCITY,
                vehicle_name=self.vehicle_name
            ).join()
        else:
            # 下降
            self.get_drone().moveToZAsync(
                -self.altitude - dist,
                VELOCITY,
                vehicle_name=self.vehicle_name
            ).join()

        self.altitude -= dist  # 更新高度
        time.sleep(EXECUTION_DELAY)
    @overrides
    def set_position(self, x: float, y: float, z: float = None):
        """飞到绝对位置（NED坐标系）"""
        if z is None:
            z = self.altitude  # 保持当前高度

        print(f"-> Fly to position ({x}, {y}, {z})")

        # 计算当前位置到目标位置的距离
        state = self.get_drone().getMultirotorState()
        current_pos = state.kinematics_estimated.position

        dx = x - current_pos.x_val
        dy = y - current_pos.y_val
        dz = z - current_pos.z_val

        dist = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        duration = dist / VELOCITY

        # 飞到目标位置
        self.get_drone().moveToPositionAsync(
            x, y, z,
            VELOCITY,
            duration,
            drivetrain=airsim.DrivetrainType.MaxDegreeOfFreedom,
            yaw_mode=airsim.YawMode(False, 0),
            vehicle_name=self.vehicle_name
        ).join()

        time.sleep(EXECUTION_DELAY)

class AirSimObservation(RobotObservation):
    def __init__(self, drone:AirSimWrapper, robot_info: RobotInfo, rate: int = 2):
        super().__init__(robot_info, rate)
        self.capture_thread = None
        self.drone = drone
        self.yolo_client = YoloClient(robot_info)

        # AirSim 相机配置
        self.camera_name = "0"  # 默认相机
        if "camera" in robot_info.extra:
            self.camera_name = robot_info.extra["camera"]

        self.image_type = airsim.ImageType.Scene
        if "image_type" in robot_info.extra:
            img_type = robot_info.extra["image_type"]
            if img_type == "depth":
                self.image_type = airsim.ImageType.DepthPerspective
            elif img_type == "segmentation":
                self.image_type = airsim.ImageType.Segmentation

    def capture(self):
        def _capture_spin():
            while self.running:
                try:
                    # 获取图像
                    responses = self.drone.get_drone().simGetImages([
                        airsim.ImageRequest(self.camera_name, self.image_type, False, False)
                    ])

                    if responses and len(responses) > 0:
                        response = responses[0]

                        # 转换为 PIL Image
                        if self.image_type == airsim.ImageType.DepthPerspective:
                            # 深度图像需要特殊处理
                            depth_img = airsim.list_to_2d_float_array(
                                response.image_data_float, response.width, response.height
                            )
                            # 归一化到0-255范围
                            depth_normalized = ((depth_img - depth_img.min()) /
                                                (depth_img.max() - depth_img.min() + 1e-6) * 255).astype(np.uint8)
                            self._image = Image.fromarray(depth_normalized)
                        else:
                            # RGB或分割图像
                            img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
                            img_rgb = img1d.reshape(response.height, response.width, 3)
                            self._image = Image.fromarray(img_rgb)

                    # 获取位置和姿态
                    state = self.drone.get_drone().getMultirotorState()
                    kinematics = state.kinematics_estimated

                    # 位置（NED坐标系）
                    self._position = np.array([
                        kinematics.position.x_val,
                        kinematics.position.y_val,
                        kinematics.position.z_val
                    ])

                    # 姿态（欧拉角，弧度）
                    orientation = kinematics.orientation
                    euler = airsim.to_eularian_angles(orientation)
                    self._orientation = np.array(euler)

                except Exception as e:
                    print(f"Error in AirSim observation: {e}")

                time.sleep(0.1)
            client=self.drone.get_drone()
            client.armDisarm(False)
            client.enableApiControl(False)

        self.capture_thread = threading.Thread(target=_capture_spin, daemon=True)
    @overrides
    def _start(self):
        self.capture()
        # AirSim 不需要显式开启流，但可以开启 API 控制
        self.capture_thread.start()

    @overrides
    def _stop(self):
        self.capture_thread.join()

    @overrides
    async def process_image(self, image: Image.Image):
        await self.yolo_client.detect(image)

    @overrides
    def fetch_processed_result(self) -> dict[str, Any]:
        _, object_list = self.yolo_client.latest_result
        return {
            "yolo": object_list
        }