import time
import signal
import sys

import cv2
import gi
import numpy as np

gi.require_version("Gst", "1.0")
from gi.repository import Gst


class RTSPPublisher:
    def __init__(
        self,
        camera_capture,
        rtsp_url: str,
        width: int,
        height: int,
        fps: int,
        bitrate: int,
        is_grayscale: bool = False,
    ):
        # copy params
        self.cap = camera_capture
        self.rtsp_url = rtsp_url
        self.width = width
        self.height = height
        self.fps = fps
        self.is_grayscale = is_grayscale

        self.frame_num = 0
        self.duration = int(Gst.SECOND / self.fps)

        # set color format
        if self.is_grayscale:
            self.input_format = "GRAY8"
        else:
            self.input_format = "BGR"
        
        # set bitrate string
        bitrate_str = f"bitrate={bitrate} "
        if bitrate <= 0:
            bitrate_str = ""

        # build gstreamer launch string
        self.pipeline_str = (
            "appsrc name=source "
            "is-live=true "
            "block=true "
            "format=time "
            f"caps=video/x-raw,format={self.input_format},"
            f"width={self.width},height={self.height},framerate={self.fps}/1 "
            "! videoconvert "
            "! video/x-raw,format=I420 "
            "! x264enc "
            f"{bitrate_str}"
            "speed-preset=medium "
            "tune=zerolatency "
            f"key-int-max={self.fps} "
            "! video/x-h264,profile=baseline "
            "! h264parse config-interval=1 "
            f"! rtspclientsink location={self.rtsp_url} protocols=tcp"
        )

        print("GStreamer pipeline:")
        print(self.pipeline_str)

        self.pipeline = Gst.parse_launch(self.pipeline_str)
        self.appsrc = self.pipeline.get_by_name("source")

        if self.appsrc is None:
            raise RuntimeError("Could not find appsrc named 'source'")

        self.running = False

    def start(self):
        ret = self.pipeline.set_state(Gst.State.PLAYING)

        if ret == Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("Failed to set pipeline to PLAYING")

        self.running = True
        print(f"Publishing to {self.rtsp_url}")

        try:
            self._push_loop()
        finally:
            self.stop()

    def stop(self):
        if not self.running:
            return

        self.running = False

        try:
            self.appsrc.emit("end-of-stream")
        except Exception:
            pass

        self.pipeline.set_state(Gst.State.NULL)
        print("Stopped publisher")

    def _check_bus(self):
        bus = self.pipeline.get_bus()

        while True:
            msg = bus.pop()
            if msg is None:
                break

            if msg.type == Gst.MessageType.ERROR:
                err, debug = msg.parse_error()
                print("GStreamer ERROR:", err)
                print("Debug info:", debug)
                self.running = False
                break

            elif msg.type == Gst.MessageType.WARNING:
                err, debug = msg.parse_warning()
                print("GStreamer WARNING:", err)
                print("Debug info:", debug)

            elif msg.type == Gst.MessageType.EOS:
                print("GStreamer EOS")
                self.running = False
                break

    def _push_loop(self):
        frame_interval = 1.0 / self.fps

        while self.running:
            start_time = time.time()

            self._check_bus()

            if not self.running:
                break

            ret, frame = self.cap.read()

            if not ret or frame is None:
                print("No frame available from camera")
                time.sleep(frame_interval)
                continue

            frame = self._prepare_frame(frame)

            data = frame.tobytes()
            buf = Gst.Buffer.new_allocate(None, len(data), None)
            buf.fill(0, data)

            timestamp = self.frame_num * self.duration
            buf.pts = timestamp
            buf.dts = timestamp
            buf.duration = self.duration
            buf.offset = self.frame_num

            self.frame_num += 1

            result = self.appsrc.emit("push-buffer", buf)

            if result != Gst.FlowReturn.OK:
                print("push-buffer returned:", result)
                self.running = False
                break

            elapsed = time.time() - start_time
            sleep_time = max(0.0, frame_interval - elapsed)
            time.sleep(sleep_time)

    def _prepare_frame(self, frame):
        h, w = frame.shape[:2]

        if w != self.width or h != self.height:
            frame = cv2.resize(frame, (self.width, self.height))

        if self.is_grayscale:
            if len(frame.shape) == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        return np.ascontiguousarray(frame)


def start_rtsp_publisher(
    camera_capture,
    rtsp_url: str,
    width: int,
    height: int,
    fps: int,
    bitrate: int,
    is_grayscale: bool = False,
):
    Gst.init(None)

    publisher = RTSPPublisher(
        camera_capture=camera_capture,
        rtsp_url=rtsp_url,
        width=width,
        height=height,
        fps=fps,
        bitrate=bitrate,
        is_grayscale=is_grayscale,
    )

    def handle_signal(sig, frame):
        publisher.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    publisher.start()

