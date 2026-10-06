ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}

# Remove the APL cert
RUN rm -v /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt
RUN update-ca-certificates

# Copy the commons folder
COPY commons/ commons/

# Copy the Python scripts
COPY scripts/Accessories/dummy_ros_img_publisher.py .

# Run the code
CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; python3 dummy_ros_img_publisher.py'