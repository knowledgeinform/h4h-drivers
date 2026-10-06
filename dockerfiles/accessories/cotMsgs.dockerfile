ARG IMAGE_TAG="MISSING_IMAGE_TAG"
FROM h4h-base:${IMAGE_TAG}

WORKDIR /home/cotMsg_ws

COPY . /home/cotMsg_ws

RUN pip install pyzmq pytak pyproj cryptography

COPY takbridge /home/cotMsg_ws/takbridge

ENV PYTHONPATH=/home/cotMsg_ws:$PYTHONPATH

SHELL ["/bin/bash", "-c"]
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc


CMD /bin/bash -c 'source h4h_msgs/install/setup.bash; python3 /home/cotMsg_ws/takbridge/uvp_cot_bridge.py'
