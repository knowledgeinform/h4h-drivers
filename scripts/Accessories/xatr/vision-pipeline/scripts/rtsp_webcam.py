#!/usr/bin/env python3
# --------------------------------------------------------------
# rtsp_webcam.py – RTSP server for a USB webcam on Jetson Orin
#
# Dependencies: python3-gst-1.0, libgstrtspserver-1.0-dev
# --------------------------------------------------------------

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject, GLib
import sys
import signal

# -----------------------------------------------------------------
# Configuration Section – edit to match web cam / desired stream
# -----------------------------------------------------------------
DEVICE          = "/dev/video0"
WIDTH           = 1280
HEIGHT          = 720
FRAMERATE       = 30   # fps
BITRATE         = 4000000  # 4 Mbps
MTU             = 1400   # max RTP packet size
RTSP_PORT       = 8554
STREAM_PATH     = "/webcam"   # URL will be rtsp://<host>:8554/webcam
# -----------------------------------------------------------------

# Initialise GStreamer
Gst.init(None)

class WebcamFactory(GstRtspServer.RTSPMediaFactory):
    """MediaFactory that builds a pipeline on-demand."""

    def __init__(self):
        super(WebcamFactory, self).__init__()
        self.set_shared(True)   # allow multiple clients
        # Build caps for the source – adjust if your cam only supports MJPEG
        src_caps = f"video/x-raw,format=YUY2,width={WIDTH},height={HEIGHT},framerate={FRAMERATE}/1"
        # Compose the full pipeline description string
        pipeline_desc = (
            f"v4l2src device={DEVICE} ! "
            f"capsfilter caps=\"{src_caps}\" ! "
            f"videoconvert ! "
            f"video/x-raw,format=NV12 ! "
            f"nvv4l2h264enc bitrate={BITRATE} ! "
            f"h264parse ! "
            f"rtph264pay config-interval=1 name=pay0 pt=96 mtu={MTU}"
        )
        self.set_launch(pipeline_desc)
        # Low latency (no buffering)
        self.set_latency(0)

def main():
    # Create the RTSP server
    server = GstRtspServer.RTSPServer()
    server.props.service = str(RTSP_PORT)

    # Create mount points and add our factory
    mounts = server.get_mount_points()
    factory = WebcamFactory()
    mounts.add_factory(STREAM_PATH, factory)

    # Optional - add basic authentication to rtsp stream
    # auth = GstRtspServer.RTSPAuth()
    # token = auth.make_basic_token("viewer", "myStrongPass")
    # policy = GstRtspServer.RTSPSimpleAuthPolicy()
    # policy.add_user(token)
    # auth.set_default_policy(policy)
    # server.set_auth(auth)

    # Start the server
    server.attach(None)
    print(f"RTSP server active at rtsp://<this‑ip>:{RTSP_PORT}{STREAM_PATH}")

    # Keep the main loop running; allow graceful exit on SIGINT/SIGTERM
    loop = GLib.MainLoop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, sig, loop.quit)
    loop.run()

if __name__ == '__main__':
    main()