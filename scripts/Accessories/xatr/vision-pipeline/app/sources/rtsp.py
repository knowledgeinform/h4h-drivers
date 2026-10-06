from __future__ import annotations

import cv2

from app.sources.base import FrameSource


class RTSPSource(FrameSource):
    def __init__(self, url: str) -> None:
        self.url = url
        self.cap = None


    def open(self) -> None:
        pipeline = (
            f'rtspsrc location="{self.url}" '
            "latency=0 "
            "drop-on-latency=true "
            "protocols=udp "
            "! rtph265depay "
            "! h265parse "
            "! avdec_h265 "
            "! videoconvert "
            "! video/x-raw,format=BGR "
            "! appsink "
            "max-buffers=1 "
            "drop=true "
            "sync=false"
        )

        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open RTSP stream: {self.url}")

    def read(self):
        if self.cap is None:
            raise RuntimeError("RTSP source not opened")
        return self.cap.read()

    def grab(self):
        return self.cap.grab()

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None