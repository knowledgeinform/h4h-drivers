ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}

# Install python dependencies
RUN pip3 install --cert /etc/ssl/certs/ca-certificates.crt --timeout=1000 pyzmq 

# Remove the APL cert
RUN rm -v /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt
RUN update-ca-certificates

# Copy the commons folder
COPY commons/ commons/

# Copy the Python scripts
COPY scripts/ControllerInterfaces/DummyWaypointSender.py .

# Run the code
CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; python3 DummyWaypointSender.py'