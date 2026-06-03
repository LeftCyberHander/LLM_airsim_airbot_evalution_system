# report_generator.py
import json
import matplotlib.pyplot as plt
import matplotlib
# 强制禁用 Tkinter，使用无界面后端，彻底解决线程冲突
matplotlib.use('Agg')
from typing import Dict
import os


def generate_evaluation_report(test_results: Dict, save_path: str):
    """生成可视化评测报告（HTML + 图表）"""
    # 1. 提取核心指标用于可视化
    scenario_ids = list(test_results.keys())
    task_completion_rates = [test_results[s]["metrics"]["task_completion_rate"] for s in scenario_ids]
    avg_planning_times = [test_results[s]["metrics"]["avg_planning_time"] for s in scenario_ids]
    vision_accuracies = [test_results[s]["metrics"]["vision_recognition_accuracy"] for s in scenario_ids]

    # 2. 生成图表
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 支持中文
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    task_com=len([x for x in scenario_ids if test_results[x]["metrics"]["task_completion_rate"]==100])
    # 任务完成率
    ax1.bar("完成率", task_com/len(task_completion_rates)*100, color="green")
    ax1.set_title("场景任务完成率")
    ax1.set_ylabel("完成率 (%)")
    ax1.set_ylim(0, 100)

    # LLM规划耗时
    ax2.plot(scenario_ids, avg_planning_times, marker="o", color="blue")
    ax2.set_title("各场景LLM平均规划耗时")
    ax2.set_ylabel("耗时 (秒)")

    # 视觉识别准确率
    ax3.bar(scenario_ids, vision_accuracies, color="orange")
    ax3.set_title("各场景视觉识别准确率")
    ax3.set_ylabel("准确率 (%)")
    ax3.set_ylim(0, 100)

    # 路径偏差
    avg_path_deviations = [test_results[s]["metrics"]["avg_path_deviation"] for s in scenario_ids]
    ax4.plot(scenario_ids, avg_path_deviations, marker="x", color="red")
    ax4.set_title("各场景平均路径偏差")
    ax4.set_ylabel("偏差 (米)")

    plt.tight_layout()
    chart_path = "static/evaluation_chart.png"
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path)
    plt.close()
    "avg_location_error"
    # 3. 生成HTML报告
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>无人机自主任务评测报告</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .metric-card {{ border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .scenario-section {{ margin: 20px 0; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <h1>无人机自主任务评测报告</h1>
        <h2>整体评测图表</h2>
        <img src="evaluation_chart.png" alt="评测指标图表">

        <h2>各场景详细结果</h2>
        {''.join([_generate_scenario_section(test_results[s]) for s in scenario_ids])}

        <h2>原始数据（JSON）</h2>
        <pre>{json.dumps(test_results, indent=4, ensure_ascii=False)}</pre>
    </body>
    </html>
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    # 写入HTML文件
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(html_template)


def _generate_scenario_section(scenario_result: Dict) -> str:
    """生成单个场景的HTML章节"""
    scenario_id = scenario_result["scenario_info"]["scenario_id"]
    task_desc = scenario_result["scenario_info"]["task_description"]
    metrics = scenario_result["metrics"]
    is_completed = scenario_result["is_completed"]
    # 安全处理 None 值，避免格式化报错
    location_items = ''.join([
        f"<li>{loc:.2f} 米</li>" if loc is not None else "<li>无数据</li>"
        for loc in metrics.get("location", [])
    ])
    return f"""
    <div class="scenario-section">
        <h3>场景 {scenario_id}: {task_desc}</h3>
        <div class="metric-card">
            <p><strong>任务完成状态:</strong> {"完成" if is_completed else "未完成"}</p>
            <p><strong>任务完成率:</strong> {metrics["task_completion_rate"]:.2f}%</p>
            <p><strong>LLM平均规划耗时:</strong> {metrics["avg_planning_time"]:.2f} 秒</p>
            <p><strong>LLM指令理解准确率:</strong> {metrics["llm_understanding_accuracy"]:.2f}%</p>
            <p><strong>视觉识别准确率:</strong> {metrics["vision_recognition_accuracy"]:.2f}%</p>
            <p><strong>目标定位:</strong></p>
            <ul>{location_items}</ul>
            <p><strong>平均路径偏差:</strong> {metrics["avg_path_deviation"]:.2f} 米</p>
            <p><strong>系统异常率:</strong> {metrics["exception_rate"]:.4f} 次/小时</p>
        </div>
    </div>
    """