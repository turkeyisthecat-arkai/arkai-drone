from dataclasses import dataclass

from arkai_drone.sensing.camera_manager import CameraFrame


@dataclass(slots=True)
class PerceptionOutput:
    obstacles: list[tuple[float, float, float]]
    free_space_score: float


class LocalPerceptionEngine:
    """Placeholder for TensorRT/ONNX runtime accelerated inference."""

    def infer(self, frames: list[CameraFrame]) -> PerceptionOutput:
        if not frames:
            return PerceptionOutput(obstacles=[], free_space_score=0.0)
        return PerceptionOutput(obstacles=[(3.5, 0.2, 0.5)], free_space_score=0.83)
