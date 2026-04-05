# ARKAI Autonomous AI Drone Architecture

## 1. Mission Objective
Build a fully autonomous intelligent drone stack that runs on **Jetson Orin Nano**, integrates **PX4/ArduPilot**, performs **local AI inference**, and executes real-time obstacle avoidance with a **multi-camera + LiDAR + GPS + IMU** sensor suite, plus close-range ultrasonic safety sensing.

## 2. High-Level System Layers

1. **Hardware Layer**
   - Flight controller: PX4 or ArduPilot compatible board.
   - Companion computer: Jetson Orin Nano.
   - Sensors: front/rear/down cameras (+ optional side cameras), LiDAR, ultrasonic, GNSS (GPS), IMU.

2. **Middleware + Communication Layer**
   - Internal pub/sub event bus for low-latency module communication.
   - Message schemas for sensor frames, state estimates, trajectories, and flight commands.
   - MAVLink transport through autopilot adapters.

3. **Perception + AI Layer**
   - Multi-camera perception (detection/segmentation/depth estimation).
   - LiDAR obstacle extraction.
   - Sensor fusion (GPS+IMU+LiDAR+ultrasonic+vision).
   - On-device inference acceleration (TensorRT/ONNX Runtime on Jetson).

4. **Decision + Navigation Layer**
   - Global mission planner and local trajectory planner.
   - Obstacle avoidance and fail-safe behavior.
   - Health monitor and degraded-mode handling.

5. **Control Layer**
   - Autopilot adapter to PX4/ArduPilot.
   - Command generation: attitude, velocity, position setpoints.
   - Telemetry and command acknowledgement loop.

## 3. Runtime Data Flow

1. `sensing/*` publishes raw sensor packets.
2. `sensing/fusion.py` produces a unified state estimate.
3. `ai/perception.py` outputs detected objects and free-space constraints.
4. `ai/avoidance.py` updates safety constraints.
5. `ai/decision_engine.py` selects autonomous mission behavior.
6. `navigation/planner.py` computes desired trajectory.
7. `autopilot/*_adapter.py` converts trajectory to FCU commands, handles telemetry, and mode switching.
8. `comm/telemetry.py` emits status to ground station.

## 4. Communication Design

- **Core pattern**: topic-based publish/subscribe.
- **Message envelope**:
  - `topic`
  - `timestamp`
  - `source`
  - typed payload.
- **Transport options**:
  - In-process queue bus for development/simulation.
  - ZeroMQ transport for distributed services on Jetson.
  - MAVLink for FCU command/telemetry exchange.

## 5. Safety + Reliability

- Geofence and altitude ceiling checks.
- Loss-of-sensor and stale-data detection.
- Autopilot heartbeat watchdog.
- Emergency fallback behavior:
  1. Hover,
  2. Return-to-home,
  3. Land.

## 6. Deployment Strategy

- Containerized services per module where possible.
- Systemd services for boot-time bring-up on Jetson.
- Simulation first (SITL), then HITL, then field flight tests.

## 7. Suggested Iteration Plan

1. Establish communication bus + module contracts.
2. Integrate PX4 (or ArduPilot) SITL and mission command path.
3. Add multi-camera + LiDAR ingest pipeline.
4. Add AI perception model and avoider.
5. Harden with watchdogs, fail-safes, and mission-level tests.
