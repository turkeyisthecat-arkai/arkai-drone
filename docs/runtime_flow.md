# Runtime Flow (Simulation-Ready)

## 1. Startup
1. `runtime.main` configures logging.
2. Runtime loads `DroneSettings` from defaults or a JSON/TOML file.
3. Autopilot adapter is selected (`px4` or `ardupilot`) and connected.
4. `DroneOrchestrator` is initialized with sensing, fusion, perception, avoidance, planner, mission manager, and safety watchdog components.

## 2. Per-cycle pipeline
For each control cycle (`control_hz`):
1. Capture camera frames and read LiDAR/GPS/IMU.
2. Fuse sensor data into `StateEstimate`.
3. Run perception model stub for obstacle/free-space cues.
4. Run safety watchdog checks:
   - stale sensor data,
   - invalid GPS,
   - LiDAR missing,
   - heartbeat timeout,
   - geofence breach.
5. Produce avoidance decision from minimum obstacle distance.
6. Generate planner command using mission context and safety fallback state.
7. Send trajectory command through autopilot adapter.
8. Write telemetry and runtime status snapshot files.

## 3. Safety fallback policy
- `continue`: nominal control path.
- `hover`: hold position when sensors are incomplete/degraded.
- `return_to_home`: geofence breach with return-home enabled.
- `land`: heartbeat timeout (highest-priority failsafe).

## 4. Mission framework
Mission manager supports starter mission types:
- `idle`
- `waypoint_patrol`
- `observe_target_area`
- `return_home`

Transitions are explicit (`set_mission`, `advance_if_reached`, `mark_target_observed`, `trigger_return_home`) and exposed through status snapshots for observability.

## 5. Observability model
The runtime emits:
- structured log events (`startup`, `sensor_reads`, `fusion_state`, `avoidance_decision`, `planner_output`, `autopilot_command`, failures),
- `telemetry_snapshot.json` for per-cycle machine-readable telemetry,
- `runtime_status.json` for quick health/status inspection.
