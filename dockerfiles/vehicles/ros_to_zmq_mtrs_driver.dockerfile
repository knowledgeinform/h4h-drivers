ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}

# Install python dependencies
RUN pip install --cert /etc/ssl/certs/ca-certificates.crt pyzmq

# Remove the APL cert
RUN rm -v /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt
RUN update-ca-certificates

# Copy the commons folder
COPY commons/ commons/

# Copy the Python scripts and resources
COPY scripts/VehicleInterfaces/zmq_driver_node.py .

# Run the code
CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; python3 zmq_driver_node.py'

