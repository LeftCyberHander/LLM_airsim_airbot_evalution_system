from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class DroneTaskScenario:
    #无人机任务配置
    scenario_id: str          # ID
    task_description: str     # 任务自然语言描述
    target_objects: List[str] # 目标物体列表
    env_params: dict          # 环境参数
    drone_init_pose: Tuple[float, float, float] # 无人机初始（x,y,z）
    timeout: int = 300        # 任务超时时间（秒）

# 示例场景库
def get_default_scenarios() -> List[DroneTaskScenario]:
    return [
    # ==================== 20个 简单任务（无物体识别 · 纯基础飞行）S001-S020 ====================
    DroneTaskScenario(
        scenario_id="S001",
        task_description="原地悬停10秒",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 0, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S002",
        task_description="直线向前飞行2米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 1, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S003",
        task_description="垂直上升至2米高度",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 0, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S004",
        task_description="垂直下降至0.5米高度",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 0, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S005",
        task_description="原地顺时针旋转90度",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 1, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S006",
        task_description="原地逆时针旋转90度",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 1, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S007",
        task_description="向左水平飞行1米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 1, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S008",
        task_description="向右水平飞行1米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 1, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S009",
        task_description="向后飞行2米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 2, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S010",
        task_description="低空1米高度定高飞行",
        target_objects=["none"],
        env_params={"light_intensity": "low", "obstacles": 0, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S011",
        task_description="高空2.5米高度定高飞行",
        target_objects=["none"],
        env_params={"light_intensity": "high", "obstacles": 0, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S012",
        task_description="小半径原地盘旋1圈",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 2, "space_size": "6x6x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S013",
        task_description="向前飞行2米后返回起点",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 1, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S014",
        task_description="连续垂直升降2次",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 0, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S015",
        task_description="缓慢向前飞行1米",
        target_objects=["none"],
        env_params={"light_intensity": "low", "obstacles": 1, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S016",
        task_description="斜向前方飞行2米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 2, "space_size": "6x6x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S017",
        task_description="水平定高巡航3米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 1, "space_size": "6x6x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S018",
        task_description="起飞后稳定悬停",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 0, "space_size": "5x5x3m"},
        drone_init_pose=(0.0, 0.0, 0.5),
    ),
    DroneTaskScenario(
        scenario_id="S019",
        task_description="向左前方飞行1.5米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 2, "space_size": "6x6x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S020",
        task_description="向右前方飞行1.5米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 2, "space_size": "6x6x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),

    # ==================== 10个 中等任务（无复杂识别 · 基础航线飞行）S021-S030 ====================
    DroneTaskScenario(
        scenario_id="S021",
        task_description="飞行正方形航线（边长2米）",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 3, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S022",
        task_description="绕定点缓慢圆周飞行",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 3, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S023",
        task_description="高度从1米渐变至2米飞行",
        target_objects=["none"],
        env_params={"light_intensity": "low", "obstacles": 2, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S024",
        task_description="沿场地边界慢速飞行",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 4, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S025",
        task_description="S型航线飞行3米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 3, "space_size": "8x8x4m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S026",
        task_description="斜向长距离飞行4米",
        target_objects=["none"],
        env_params={"light_intensity": "high", "obstacles": 3, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S027",
        task_description="低速绕开简单障碍物飞行",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 5, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S028",
        task_description="矩形航线巡航飞行",
        target_objects=["none"],
        env_params={"light_intensity": "low", "obstacles": 4, "space_size": "8x8x4m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S029",
        task_description="两点之间往返飞行2次",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 3, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S030",
        task_description="定高直线飞行5米",
        target_objects=["none"],
        env_params={"light_intensity": "medium", "obstacles": 4, "space_size": "10x10x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),

    # ==================== 8个 识别物体+运动任务（低难度 · 简单识别+基础运动）S031-S038 ====================
    DroneTaskScenario(
        scenario_id="S031",
        task_description="识别树木后在旁边悬停",
        target_objects=["tree"],
        env_params={"light_intensity": "medium", "obstacles": 5, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S032",
        task_description="识别石头后飞行至石头旁",
        target_objects=["stone"],
        env_params={"light_intensity": "low", "obstacles": 5, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S033",
        task_description="识别树桩后环绕飞行1圈",
        target_objects=["stump"],
        env_params={"light_intensity": "medium", "obstacles": 6, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S034",
        task_description="识别灌木后低空飞过",
        target_objects=["bush"],
        env_params={"light_intensity": "medium", "obstacles": 5, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    ),
    DroneTaskScenario(
        scenario_id="S035",
        task_description="识别空地后飞行至空地中心",
        target_objects=["empty_ground"],
        env_params={"light_intensity": "medium", "obstacles": 4, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S036",
        task_description="识别树干后靠近至1米处",
        target_objects=["trunk"],
        env_params={"light_intensity": "low", "obstacles": 6, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.5),
    ),
    DroneTaskScenario(
        scenario_id="S037",
        task_description="识别草丛后在上方悬停",
        target_objects=["grass"],
        env_params={"light_intensity": "medium", "obstacles": 5, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.2),
    ),
    DroneTaskScenario(
        scenario_id="S038",
        task_description="识别石块后低空掠过",
        target_objects=["rock"],
        env_params={"light_intensity": "medium", "obstacles": 6, "space_size": "8x8x3m"},
        drone_init_pose=(0.0, 0.0, 1.0),
    )
]