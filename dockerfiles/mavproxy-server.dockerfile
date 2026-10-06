FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# install dependencies
RUN apt-get update
RUN apt-get install -y python3-dev 
RUN apt-get install -y python3-opencv
RUN apt-get install -y python3-wxgtk4.0 
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-matplotlib 
RUN apt-get install -y python3-lxml 
RUN apt-get install -y python3-pygame

# install mavproxy
RUN python3 -m pip install PyYAML mavproxy
# RUN echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc

# remove modemmanager
RUN apt-get purge -y modemmanager
RUN apt-get autoremove -y

# enable dialout
# RUN usermod -a -G dialout $USER

# install additional python dependencies that mavproxy misses
RUN python3 -m pip install future

# Copy the APL cert
# COPY resources/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt /usr/local/share/ca-certificates/

# Update system certificates
# RUN update-ca-certificates

# copy the mavproxy run script
COPY scripts/Accessories/start-mavproxy.sh start-mavproxy.sh
RUN chmod +x start-mavproxy.sh

# run the mavproxy command
CMD ./start-mavproxy.sh
