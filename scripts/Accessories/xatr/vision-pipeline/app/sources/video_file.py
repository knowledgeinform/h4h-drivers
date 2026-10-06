from __future__ import annotations

import cv2

from app.sources.base import FrameSource


class VideoFileSource(FrameSource):
    def __init__(self, path: str) -> None:
        self.path = path
        self.cap = None

    def open(self) -> None:
        self.cap = cv2.VideoCapture(self.path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open video file: {self.path}")

    def read(self):
        if self.cap is None:
            raise RuntimeError("Video file not opened")
        return self.cap.read()

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None