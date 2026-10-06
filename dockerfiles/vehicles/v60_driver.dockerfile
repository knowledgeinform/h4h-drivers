ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}

RUN pip install pyzmq

# Remove the APL cert
RUN rm -v /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt
RUN update-ca-certificates

# Copy the commons folder
COPY commons/ commons/

# Copy the Python scripts
COPY scripts/VehicleInterfaces/updated_v60_node.py .
COPY /scripts/ControllerInterfaces/RosToZmq.py . 

# Run the code
CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; python3 updated_v60_node.py'