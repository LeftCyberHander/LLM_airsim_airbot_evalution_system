import io, time, json, os, queue
from flask import Flask, Response, render_template, request, jsonify
from twisted.python.util import println

from typefly.eval.auto_test import DroneAutoTester
from typefly.eval.scenario import get_default_scenarios
from typefly.platforms.airsim_wrapper import AirSimWrapper
from typefly.robot_info import RobotInfo
from typefly.utils import print_t, CURRENT_PROJ_DIR
from typefly.llm_controller import LLMController, _USER_LOG_QUEUE

class TypeFly:
    def __init__(self, robot_info: RobotInfo):
        self.llm_controller = LLMController(robot_info)
        self.running = True
        self.app = Flask(__name__,template_folder=os.path.join(CURRENT_PROJ_DIR, 'assets'))
        self.auto_tester = DroneAutoTester(self.llm_controller.planner, self.llm_controller.robot, self.llm_controller.robot.obs.yolo_client,self.llm_controller)
        self.setup_routes()

    def setup_routes(self):
        # 新增评测页面路由
        @self.app.route("/e")
        def evaluation_page():
            return render_template("evaluation.html", scenarios=get_default_scenarios())

        # 新增执行单个场景测试的API
        @self.app.route("/run_scenario", methods=["POST"])
        def run_scenario():
            scenario_id = request.json.get("scenario_id")
            scenarios = get_default_scenarios()
            target_scenario = next((s for s in scenarios if s.scenario_id == scenario_id), None)
            if not target_scenario:
                return jsonify({"status": "error", "message": "场景不存在"})

            result = self.auto_tester.run_single_scenario(target_scenario)
            return jsonify({
                "status": "success",
                "scenario_id": scenario_id,
                "metrics": result["metrics"],
                "is_completed": result["is_completed"]
            })

        # 新增批量执行测试的API
        @self.app.route("/run_batch_scenarios", methods=["POST"])
        def run_batch_scenarios():
            scenarios = get_default_scenarios()
            self.auto_tester.run_batch_scenarios(scenarios[10:20], "static/evaluation_report.html")
            return jsonify({
                "status": "success",
                "report_url": "/static/evaluation_report.html"
            })

        """Sets up the Flask routes."""
        
        @self.app.route('/')
        def index():
            return render_template('deepseek_index.html')
        
        @self.app.route('/chat', methods=['POST'])
        def chat():
            """Handle chat messages and stream responses using SSE."""
            data = request.get_json()
            user_message = data.get('message', '')
            
            if not user_message:
                return jsonify({'type': 'text', 'content': '[WARNING] Empty command!'})
            
            if user_message == "exit":
                self.running = False
                return jsonify({'type': 'text', 'content': 'Shutting down...'})
            
            # Send instruction to LLM Controller
            self.llm_controller.put_instruction(user_message)
            
            def generate():
                # Send initial acknowledgment
                yield f"data: {json.dumps({'type': 'text', 'content': 'Okay! Working on it...'})}\n\n"
                
                # Stream messages from the queue as they arrive
                while True:
                    try:
                        msg = _USER_LOG_QUEUE.get(timeout=3.0)
                        if msg == '#end':
                            print_t("[UI] End of plan")
                            return "data: [DONE]\n\n"
                    
                    except queue.Empty:
                        continue

                    print_t(f"[UI] New message: {msg}")
                    msg_str = str(msg)
                    
                    # Check if message contains an image (base64 encoded)
                    if '<img src="data:image/' in msg_str:
                        # For images, we need to ensure JSON encoding doesn't break the HTML
                        response_data = json.dumps({'type': 'image', 'content': msg_str}, ensure_ascii=False)
                        yield f"data: {response_data}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'text', 'content': msg_str})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        
        @self.app.route('/robot-pov/')
        def video_feed_pov():
            """Stream robot POV video feed."""
            return Response(
                self.generate_mjpeg_stream('pov'),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        
        @self.app.route('/health')
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'running', 'robot': self.running})

        @self.app.route('/api/airsim/level_list', methods=['GET'])
        def airsim_level_list():
            robot = self.llm_controller.robot
            if not hasattr(robot, 'level_list'):
                return jsonify({'error': 'Not an AirSim robot'}), 400
            return jsonify({'level_list': robot.level_list})

        @self.app.route('/api/airsim/change_level', methods=['POST'])
        def airsim_change_level():
            robot = self.llm_controller.robot
            if not hasattr(robot, 'change_level'):
                return jsonify({'error': 'Not an AirSim robot'}), 400
            data = request.get_json()
            level_name = data.get('level_name')
            if not level_name:
                return jsonify({'error': 'level_name required'}), 400
            try:
                robot.change_level(level_name)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/airsim/create_drone', methods=['POST'])
        def airsim_create_drone():
            robot = self.llm_controller.robot
            if not hasattr(robot, 'create_drone'):
                return jsonify({'error': 'Not an AirSim robot'}), 400
            data = request.get_json()
            drone_id = data.get('drone_id')
            drone_type = data.get('drone_type')
            if drone_id is None or drone_type is None:
                return jsonify({'error': 'drone_id and drone_type required'}), 400
            try:
                drone_type = int(drone_type)
            except ValueError:
                return jsonify({'error': 'drone_type must be integer'}), 400
            try:
                println(drone_type)
                result = robot.create_drone(drone_id, drone_type)
                return jsonify({'success': True, 'result': str(result)})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/airsim/robot_list', methods=['GET'])
        def airsim_robot_list():
            return jsonify({'robot_list': AirSimWrapper.robot_list})

        @self.app.route('/api/airsim/set_name', methods=['POST'])
        def airsim_set_name():
            robot = self.llm_controller.robot
            if not hasattr(robot, 'set_name'):
                return jsonify({'error': 'Not an AirSim robot'}), 400
            data = request.get_json()
            name = data.get('name')
            if not name:
                return jsonify({'error': 'name required'}), 400
            try:
                robot.set_name(name)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                # ---------- AirSim specific endpoints ----------

    def generate_mjpeg_stream(self, source: str):
        """Generate MJPEG stream for video feeds."""
        while self.running:
            if source == 'pov':
                frame = self.llm_controller.fetch_robot_pov()
            else:
                frame = None
            
            if frame is None:
                time.sleep(1.0 / 30.0)
                continue
                
            buf = io.BytesIO()
            frame.save(buf, format='JPEG')
            buf.seek(0)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buf.read() + b'\r\n')
            time.sleep(1.0 / 30.0)
        # ---------- AirSim specific endpoints ----------
    def run(self):
        """Start the TypeGo system with Flask server."""
        # Start the LLM controller
        self.llm_controller.start_controller()

        # Start the Flask server
        print_t("[TypeGo] Starting Flask server on http://0.0.0.0:50000")
        self.app.run(host='127.0.0.1', port=50000, debug=False, threaded=True)
        
        # When Flask stops, stop the LLM controller
        self.llm_controller.stop_controller()

def main():
    with open(os.path.join(CURRENT_PROJ_DIR, 'config/robot_info.json'), 'r') as f:
        typefly = TypeFly(RobotInfo.from_dict(json.load(f)))
        typefly.run()

if __name__ == '__main__':
    os.environ["OPENAI_API_KEY"]="xxx"
    main()