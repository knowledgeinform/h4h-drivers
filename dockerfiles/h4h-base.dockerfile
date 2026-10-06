# Start with a ROS2 Humble (Ubuntu 22.04) with rosdep installed
FROM ros:humble-ros-base

RUN rm /etc/apt/sources.list.d/ros2.list || true
RUN rm /usr/share/keyrings/ros-archive-keyring.gpg || true 

# Update apt
RUN apt-get update

# Use Cyclone DDS as middleware
RUN apt-get install -y --no-install-recommends \
 ros-${ROS_DISTRO}-rmw-cyclonedds-cpp
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Install ROS message types
RUN apt-get install -y ros-humble-geographic-info ros-humble-geographic-msgs
RUN apt-get install -y ros-humble-sensor-msgs
RUN apt-get install -y ros-humble-mavros-msgs

# Install pip
RUN apt-get install -y python3-pip

# Make Python print unbuffered
ENV PYTHONUNBUFFERED=1

# Copy the APL cert
COPY resources/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt /usr/local/share/ca-certificates/

# Update system certificates
RUN update-ca-certificates

# Install Opencv Lib dependencies
RUN apt-get install -y ffmpeg libsm6 libxext6

# Install python dependencies
RUN pip3 install --cert /etc/ssl/certs/ca-certificates.crt opencv-python cv-bridge utm pyzmq
RUN pip3 install --cert /etc/ssl/certs/ca-certificates.crt --upgrade typing-extensions

# Copy the ROS2 packages 
## TODO when there is time and budget 
COPY h4h_msgs h4h_msgs/h4h_msgs 
COPY ghost_manager_interfaces h4h_msgs/ghost_manager_interfaces 
# COPY h4h_msgs/msg h4h_msgs/msg
# COPY h4h_msgs/CMakeLists.txt h4h_msgs/CMakeLists.txt
# COPY h4h_msgs/package.xml h4h_msgs/package.xml

# Copy the commons folder
# COPY commons/ commons/

# Build the package
RUN /bin/bash -c '. /opt/ros/humble/setup.bash; cd h4h_msgs; colcon build'

# Add the desired ROS_NAMESPACE
ENV ROS_NAMESPACE="rlac_h4h"
ENV ROS_DOMAIN_ID=123
