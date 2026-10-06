ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}


# Copy the commons folder
COPY commons/ commons/

COPY scripts/gps_publishing_test/sim_gps_stream_to_ros.py .

CMD /bin/bash -c "source h4h_msgs/install/setup.bash; python3 sim_gps_stream_to_ros.py"
