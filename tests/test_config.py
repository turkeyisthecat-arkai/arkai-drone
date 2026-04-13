import json

from arkai_drone.config.settings import load_settings


def test_load_settings_json(tmp_path) -> None:
    config = {
        "autopilot": "ardupilot",
        "control_hz": 20,
        "geofence_radius_m": 150.0,
        "simulation_mode": True,
        "cameras": ["front"],
    }
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    settings = load_settings(path)

    assert settings.autopilot == "ardupilot"
    assert settings.control_hz == 20
    assert settings.geofence_radius_m == 150.0


def test_load_settings_toml(tmp_path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text(
        '\n'.join(
            [
                'autopilot = "px4"',
                "control_hz = 25",
                "perception_hz = 10",
                "obstacle_distance_m = 2.5",
                "max_velocity_mps = 4.0",
                "geofence_radius_m = 120.0",
                "return_to_home_enabled = true",
                "simulation_mode = true",
                'cameras = ["front", "down"]',
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(path)

    assert settings.control_hz == 25
    assert settings.cameras == ["front", "down"]
