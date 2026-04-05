from arkai_drone.ai.avoidance import ObstacleAvoider
from arkai_drone.ai.perception import LocalPerceptionEngine
from arkai_drone.autopilot.adapter import AutopilotAdapter
from arkai_drone.config.settings import DroneSettings
from arkai_drone.navigation.planner import LocalPlanner
from arkai_drone.sensing.camera_manager import MultiCameraSystem
from arkai_drone.sensing.fusion import SensorFusion
from arkai_drone.sensing.gps import GPSSensor
from arkai_drone.sensing.imu import IMUSensor
from arkai_drone.sensing.lidar import LidarSensor


class DroneOrchestrator:
    def __init__(self, settings: DroneSettings, autopilot: AutopilotAdapter) -> None:
        self.settings = settings
        self.autopilot = autopilot
        self.cameras = MultiCameraSystem(settings.cameras)
        self.lidar = LidarSensor()
        self.gps = GPSSensor()
        self.imu = IMUSensor()
        self.fusion = SensorFusion()
        self.perception = LocalPerceptionEngine()
        self.avoider = ObstacleAvoider(settings.obstacle_distance_m)
        self.planner = LocalPlanner()

    def step(self) -> None:
        frames = self.cameras.capture()
        lidar_scan = self.lidar.read()
        gps_fix = self.gps.read()
        imu_sample = self.imu.read()

        state = self.fusion.fuse(gps_fix, imu_sample, lidar_scan)
        _perception = self.perception.infer(frames)
        avoidance = self.avoider.decide(
            obstacle_distance_m=state.obstacle_min_distance_m,
            nominal_speed_mps=self.settings.max_velocity_mps,
        )
        command = self.planner.next_command(state, avoidance)
        self.autopilot.send_trajectory(command)
