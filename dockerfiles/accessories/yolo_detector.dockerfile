ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}

# Install apt dependencies
RUN apt-get install -y ffmpeg libsm6 libxext6

# Install python dependencies
RUN pip3 install --cert /etc/ssl/certs/ca-certificates.crt opencv-python cv-bridge

# Remove the APL cert
RUN rm -v /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt
RUN update-ca-certificates

# Copy the commons folder
COPY commons/ commons/

# Copy the Python scripts and resources
COPY scripts/ObjectDetectors/detector_base.py .
COPY scripts/ObjectDetectors/yolo_detector.py .
COPY scripts/ObjectDetectors/yolo.py .

COPY scripts/ObjectDetectors/configs/yolov3.cfg .
COPY scripts/ObjectDetectors/configs/yolov3.weights .
COPY scripts/ObjectDetectors/configs/coco.names .

# Run the code
CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; python3 yolo_detector.py'

