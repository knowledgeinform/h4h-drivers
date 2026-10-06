ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3-pip \
      python3-serial \
      socat \
      ros-humble-rclpy \
      ros-humble-sensor-msgs && \
    rm -rf /var/lib/apt/lists/*

#Python GPS parsing lib
RUN pip3 install pynmea2

COPY scripts/gps_publishing_test/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy the commons folder
COPY commons/ commons/

COPY scripts/gps_publishing_test/gps_stream_to_ros.py .

# entrypoint will launch socat
ENTRYPOINT ["/entrypoint.sh"]
CMD /bin/bash -c "source h4h_msgs/install/setup.bash; python3 gps_stream_to_ros.py /dev/ttyUSB0 9600 --ros-topic /gps/fix --frame-id gps_link"
