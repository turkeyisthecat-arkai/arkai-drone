from dataclasses import dataclass


@dataclass(slots=True)
class AvoidanceDecision:
    limit_velocity_mps: float
    avoid_vector_xyz: tuple[float, float, float]


class ObstacleAvoider:
    def __init__(self, safety_distance_m: float) -> None:
        self.safety_distance_m = safety_distance_m

    def decide(self, obstacle_distance_m: float, nominal_speed_mps: float) -> AvoidanceDecision:
        if obstacle_distance_m < self.safety_distance_m:
            return AvoidanceDecision(
                limit_velocity_mps=max(1.0, nominal_speed_mps * 0.4),
                avoid_vector_xyz=(-1.0, 0.0, 0.0),
            )
        return AvoidanceDecision(limit_velocity_mps=nominal_speed_mps, avoid_vector_xyz=(0.0, 0.0, 0.0))
