from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class CameraFrame:
    camera_id: str
    frame_id: int
    width: int
    height: int
    encoded: bytes


class CameraDriver(Protocol):
    def capture(self) -> bytes: ...


class MockCameraDriver:
    def __init__(self, camera_id: str) -> None:
        self.camera_id = camera_id
        self._counter = 0

    def capture(self) -> bytes:
        self._counter += 1
        return f"{self.camera_id}:{self._counter}".encode()


class MultiCameraSystem:
    """Unified multi-camera interface for front/rear/down/(optional) side cameras."""

    REQUIRED_CAMERAS = ("front", "rear", "down")

    def __init__(self, camera_ids: list[str], drivers: dict[str, CameraDriver] | None = None) -> None:
        requested = set(camera_ids)
        missing_required = [camera_id for camera_id in self.REQUIRED_CAMERAS if camera_id not in requested]
        if missing_required:
            msg = f"Missing required cameras: {', '.join(missing_required)}"
            raise ValueError(msg)

        self.camera_ids = camera_ids
        self._frame_counter = 0
        self._drivers: dict[str, CameraDriver] = {
            camera_id: MockCameraDriver(camera_id) for camera_id in camera_ids
        }
        if drivers:
            self._drivers.update(drivers)

    def capture(self) -> list[CameraFrame]:
        self._frame_counter += 1
        return [
            CameraFrame(
                camera_id=camera_id,
                frame_id=self._frame_counter,
                width=1280,
                height=720,
                encoded=self._drivers[camera_id].capture(),
            )
            for camera_id in self.camera_ids
        ]
