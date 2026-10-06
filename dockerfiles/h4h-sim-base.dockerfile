# Start with a ROS2 Humble (Ubuntu 22.04) with rosdep installed
FROM ros:humble-ros-base

RUN rm /etc/apt/sources.list.d/ros2.list || true
RUN rm /usr/share/keyrings/ros-archive-keyring.gpg || true 

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

# Install Opencv Lib dependencies
RUN apt-get install -y ffmpeg libsm6 libxext6

# Install python dependencies
RUN pip3 install --cert /etc/ssl/certs/ca-certificates.crt opencv-python cv-bridge utm

#### SPLIT #### probably just use from the base, but in case stuff needs to change

# install dependencies
RUN apt-get install -y wget

# clone PX4 and run setup script
RUN git clone https://github.com/PX4/PX4-Autopilot.git --recursive
RUN chmod +x PX4-Autopilot/Tools/setup/ubuntu.sh
RUN ./PX4-Autopilot/Tools/setup/ubuntu.sh

# spin up the px4 sitl
RUN cd PX4-Autopilot && make px4_sitl
# RUN cd PX4-Autopilot && make px4_sitl gz_x500