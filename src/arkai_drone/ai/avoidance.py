from dataclasses import dataclass


@dataclass(slots=True)
class AvoidanceDecision:
    limit_velocity_mps: float
    avoid_vector_xyz: tuple[float, float, float]
    emergency_brake: bool


class ObstacleAvoider:
    def __init__(self, safety_distance_m: float, hard_stop_distance_m: float = 1.0) -> None:
        self.safety_distance_m = safety_distance_m
        self.hard_stop_distance_m = hard_stop_distance_m

    def decide(self, obstacle_distance_m: float, nominal_speed_mps: float) -> AvoidanceDecision:
        """Real-time collision prevention and path adjustment policy."""
        if obstacle_distance_m <= self.hard_stop_distance_m:
            return AvoidanceDecision(
                limit_velocity_mps=0.0,
                avoid_vector_xyz=(-2.0, 0.0, 0.5),
                emergency_brake=True,
            )

        if obstacle_distance_m < self.safety_distance_m:
            return AvoidanceDecision(
                limit_velocity_mps=max(0.8, nominal_speed_mps * 0.35),
                avoid_vector_xyz=(-1.0, 0.6, 0.2),
                emergency_brake=False,
            )

        return AvoidanceDecision(
            limit_velocity_mps=nominal_speed_mps,
            avoid_vector_xyz=(0.0, 0.0, 0.0),
            emergency_brake=False,
        )
