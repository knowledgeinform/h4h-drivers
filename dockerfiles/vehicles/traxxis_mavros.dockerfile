ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}

ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Installing Mavros
RUN apt-get update

RUN apt-get install geographiclib-tools -y

RUN wget -O - https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh | bash

RUN apt-get install -y ros-humble-mavros ros-humble-mavros-extras

RUN apt-get install -y libgstreamer-plugins-base1.0-dev

# installing transitions
RUN python3 -m pip install transitions

# # Remove the APL cert
RUN rm -v /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt
RUN update-ca-certificates

# Copy the commons folder
COPY commons/ commons/

# # copy over params
# COPY /resources/params.yaml .

# run mavros # TODO: get it into an environment variable
CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; ros2 launch mavros px4.launch fcu_url:="/dev/ttyUSB0:57600"'

# CMD /bin/bash -c 'source /opt/ros/humble/setup.bash; ros2 run mavros mavros_node --ros-args --params-file params.yaml' 
