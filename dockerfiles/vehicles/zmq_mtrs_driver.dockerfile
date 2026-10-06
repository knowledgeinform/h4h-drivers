# Start with a ROS1 Noetic with rosdep installed
# ROS1 Melodic uses Python2.7
FROM ros:noetic-robot

# Update apt
RUN apt-get update

# Install pip
RUN apt-get install -y python3-pip

# Make Python print unbuffered
ENV PYTHONUNBUFFERED=1

# Copy the APL cert
COPY resources/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt /usr/local/share/ca-certificates/

# Update system certificates
RUN update-ca-certificates

# Install catkin
RUN apt-get install -y ros-noetic-catkin python3-catkin-tools python3-osrf-pycommon

# Install python dependencies
RUN pip3 install --cert /etc/ssl/certs/ca-certificates.crt numpy==1.21
RUN pip3 install --cert /etc/ssl/certs/ca-certificates.crt pyyaml pyzmq

# Copy the ROS2 package
RUN mkdir src
COPY resource_controller_msgs src/resource_controller_msgs
COPY iop_msgs src/iop_msgs

# Build the package
RUN /bin/bash -c '. /opt/ros/noetic/setup.bash; catkin_make'
RUN /bin/bash -c 'source devel/setup.bash'

# Copy the commons folder
COPY commons/ commons/

# Copy the python script
COPY scripts/VehicleInterfaces/zmq_mtrs_driver.py .

# Run the code
CMD /bin/bash -c 'source devel/setup.bash; python3 zmq_mtrs_driver.py'