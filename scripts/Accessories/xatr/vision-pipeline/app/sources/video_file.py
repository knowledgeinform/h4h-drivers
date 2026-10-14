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

        # pre-read a frame to check for end
        ret,frame = self.cap.read()

        # rewind if at end
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return self.cap.read()
        
        # return back data
        return ret,frame

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None