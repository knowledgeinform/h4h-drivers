ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-mavros:${IMAGE_TAG}

# Install python deps
# RUN apt-get install -y python3-pip
# RUN pip install pyzmq

# copy over node script
COPY scripts/ControllerInterfaces/RosToZmq.py . 
COPY /scripts/VehicleInterfaces/mavros_ugv_node.py .

# execute node script
CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; python3 mavros_ugv_node.py' 
