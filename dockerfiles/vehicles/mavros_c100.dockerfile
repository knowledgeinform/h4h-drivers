ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-mavros:${IMAGE_TAG}

CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; ros2 launch mavros px4.launch namespace:=$ROS_NAMESPACE tgt_system:=101 fcu_url:=$(cat fcu.url)'
