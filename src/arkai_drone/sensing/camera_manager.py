from dataclasses import dataclass


@dataclass(slots=True)
class CameraFrame:
    camera_id: str
    frame_id: int
    width: int
    height: int
    encoded: bytes


class MultiCameraSystem:
    def __init__(self, camera_ids: list[str]) -> None:
        self.camera_ids = camera_ids
        self._counter = 0

    def capture(self) -> list[CameraFrame]:
        self._counter += 1
        return [
            CameraFrame(
                camera_id=camera_id,
                frame_id=self._counter,
                width=640,
                height=480,
                encoded=b"",
            )
            for camera_id in self.camera_ids
        ]
