# ARKAI Autonomous AI Drone System

Reference starter architecture and codebase for a fully autonomous intelligent drone stack targeting Jetson Orin Nano.

## Target stack
- Companion computer: Jetson Orin Nano
- Flight controllers: PX4 or ArduPilot
- Sensors: multi-camera, LiDAR, ultrasonic, GPS, IMU
- Capabilities: local AI inference, autonomous navigation, real-time obstacle avoidance

## Repository layout

```text
.
├── docs/
│   └── architecture.md
├── src/arkai_drone/
│   ├── ai/
│   ├── autopilot/
│   ├── comm/
│   ├── config/
│   ├── core/
│   ├── navigation/
│   ├── runtime/
│   └── sensing/
└── tests/
```

## Modules
- `sensing`: unified multi-camera (front/rear/down/optional side), LiDAR/GPS/IMU/ultrasonic interfaces + fusion module.
- `ai`: local perception, obstacle avoidance, and autonomous decision engine.
- `navigation`: trajectory planner + mission structures.
- `autopilot`: adapter abstraction with PX4 and ArduPilot implementations.
- `core`: orchestrator tying the autonomous loop together.
- `comm`: starter event bus and telemetry envelope.
- `runtime`: entrypoint for simulation/starter runtime.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
pytest -q
python -m arkai_drone.runtime.main
```

## Next implementation steps
1. Replace placeholder sensor drivers with CSI/USB camera and LiDAR SDK integration.
2. Integrate MAVSDK/DroneKit or direct MAVLink stack for command and telemetry (mode switching + health-aware control).
3. Add TensorRT/ONNX inference models and calibration pipeline.
4. Add mission planner, geofence, return-to-home, and safety watchdogs.
