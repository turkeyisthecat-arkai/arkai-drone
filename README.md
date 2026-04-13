# ARKAI Autonomous AI Drone System

Simulation-first autonomous drone runtime scaffold targeting Jetson Orin Nano with PX4/ArduPilot adapters.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
pytest -q
python -m arkai_drone.runtime.main --cycles 10
```

Run with a JSON/TOML config:

```bash
python -m arkai_drone.runtime.main --config ./configs/sim.toml --cycles 20
```

## Simulation mode

`DroneSettings.simulation_mode` defaults to `true`. In simulation mode:
- sensors provide deterministic stub data,
- autopilot adapters only log trajectory commands,
- safety and mission logic operate without requiring hardware SDKs.

## Runtime outputs

Every runtime cycle writes:
- **Telemetry snapshot** (`telemetry_snapshot_path`) with mode, mission state, GPS, yaw, obstacle distance, chosen command, safety state, timestamp.
- **Status snapshot** (`status_snapshot_path`) with overall runtime mode, mission status, and safety reasons.

## Module responsibilities

- `config`: dataclass settings + JSON/TOML config loader + validation.
- `sensing`: camera/LiDAR/GPS/IMU stubs + fusion state estimator.
- `ai`: perception placeholder + obstacle avoidance constraints.
- `core`: orchestrator and safety watchdog (stale sensors, GPS/LiDAR/heartbeat/geofence checks).
- `navigation`: mission model/state transitions and local planner command generation.
- `autopilot`: adapter abstraction with PX4 and ArduPilot logging implementations.
- `runtime`: CLI entrypoint, logging setup, execution loop.
- `tests`: pytest coverage for orchestration, safety, planner, mission, and config loading.

## Next recommended steps

1. Replace sensor stubs with SITL/HITL bridges while preserving current interfaces.
2. Route telemetry snapshots to a message bus or dashboard process.
3. Expand mission execution (waypoint distance checks, target observation timers, mission queues).
4. Harden safety policy with altitude ceiling, battery state, and actuator health.
5. Add integration tests for longer mission scenarios and degraded recovery.
