ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-mavros:${IMAGE_TAG}

# copy over node script
COPY /scripts/ControllerInterfaces/RosToZmq.py . 
COPY /scripts/VehicleInterfaces/c100_node.py .

# execute node script
CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; python3 c100_node.py' 
