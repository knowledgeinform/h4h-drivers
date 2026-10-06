# RTSP Setup on NVIDIA Orin

This document shows the 3 simple steps to:

1. Start the MediaMTX Docker container
2. Publish the USB webcam as an RTSP stream
3. Test the RTSP stream with `ffprobe`

---

## Prerequisites

- Docker is installed and working
- `ffmpeg` and `ffprobe` are installed
- The webcam is available as `/dev/video0`

You can verify the camera exists with:

```bash
v4l2-ctl --list-devices

## Open a terminal and Run MediaMTX Docker container (this starts the server on port 8554)

docker run --rm -it --network=host bluenviron/mediamtx:1

## Open second terminal and publish the webcam to rtsp (rtsp://localhost:8554/mystream)

ffmpeg -f v4l2 -framerate 10 -video_size 1280x720 -i /dev/video0 \
-c:v libx264 -preset veryfast -tune zerolatency -pix_fmt yuv420p \
-f rtsp rtsp://localhost:8554/mystream

## Open a third terminal to test

ffprobe -rtsp_transport tcp rtsp://localhost:8554/mystream

## Better long-term path: install the standalone ARM64 binary
## MediaMTX’s official install docs say to download the Linux binary matching your architecture and run ./mediamtx; the current site shows current releases in the 1.x line and explicitly supports Linux arm64 binaries.
## 1. download the linux_arm64 release tarball on a connected machine,
## 2. copy it to the Orin,
## 3. extract it,
## 4. run ./mediamtx.  
## 5. Then use the same FFmpeg publish command as above.