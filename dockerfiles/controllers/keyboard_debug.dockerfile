ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}

ENV PIP_DEFAULT_TIMEOUT=100
# Install python dependencies
RUN pip install --cert /etc/ssl/certs/ca-certificates.crt pynput pygame

# Remove the APL cert
RUN rm -v /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt
RUN update-ca-certificates

# Copy the Python scripts and resources
COPY ../keyboard_debug.py .

# python3 keyboard_debug.py

#CMD only pertains to initial shell instance. If we exec we need to use RUN
RUN echo "source /opt/ros/humble/setup.sh" >> ~/.bashrc && \
    echo "source /h4h_msgs/install/setup.bash" >> ~/.bashrc

    # Run the code
# also need to source opt/ros/humble/setup.sh
CMD /bin/bash -c 'source /h4h_msgs/install/setup.bash; source /opt/ros/humble/setup.sh; python3 -u keyboard_debug.py'
