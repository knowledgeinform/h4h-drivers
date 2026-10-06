from __future__ import annotations

import cv2

from app.sources.base import FrameSource


class WebcamSource(FrameSource):
    def __init__(self, device_index: int = 0) -> None:
        self.device_index = device_index
        self.cap = None

    def open(self) -> None:
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open webcam device {self.device_index}")

    def read(self):
        if self.cap is None:
            raise RuntimeError("Webcam not opened")
        return self.cap.read()

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None