# FROM ubuntu:22.04
# FROM nvcr.io/nvidia/l4t-tensorrt:r10.3.0-runtime # requires CUDA >= 12.6
# FROM nvcr.io/nvidia/l4t-tensorrt:r8.6.2-runtime # requires CUDA >= 12.2

# this is the oldest available l4t-tensorrt image
# FROM nvcr.io/nvidia/l4t-tensorrt:r8.0.1-runtime # contains CUDA 10.2

# this is the oldest available devel image # has CUDA 11.4 # supports up to CUDA Compute Capability 8.7
FROM nvcr.io/nvidia/l4t-tensorrt:r8.4.1.5-devel

# update apt
RUN apt-get update

## ** CHATGPT SECTION START (now with lots of edits because of course)**

ARG DEBIAN_FRONTEND=noninteractive
ARG OPENCV_VERSION=4.5.5
ARG OPENCV_CONTRIB_VERSION=4.5.5

# Set this to the COMPUTE CAPABILITY for your Jetson GPU (use "nvcc --list-gpu-arch" to see supported numbers)
ARG CUDA_ARCH_BIN=8.7

RUN apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    ninja-build \
    pkg-config \
    python3-dev \
    python3-numpy \
    python3-sklearn-lib \
    python3-tqdm \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libopenblas-dev \
    liblapack-dev \
    libhdf5-dev \
    gfortran

WORKDIR /xatr_opencv

RUN git clone --depth 1 --branch ${OPENCV_VERSION} \
      https://github.com/opencv/opencv.git \
      /xatr_opencv/opencv && \
    git clone --depth 1 --branch ${OPENCV_CONTRIB_VERSION} \
      https://github.com/opencv/opencv_contrib.git \
      /xatr_opencv/opencv_contrib

WORKDIR /xatr_opencv/opencv/build


RUN cmake -G Ninja \
    -D CMAKE_BUILD_TYPE=Release \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/xatr_opencv/opencv_contrib/modules \
    -D WITH_CUDA=ON \
    -D WITH_CUBLAS=ON \
    -D CUDA_FAST_MATH=ON \
    -D ENABLE_FAST_MATH=ON \
    -D CUDA_ARCH_BIN=${CUDA_ARCH_BIN} \
    -D WITH_GSTREAMER=ON \
    -D WITH_V4L=ON \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_EXAMPLES=OFF \
    -D BUILD_opencv_python3=ON \
    -D PYTHON_EXECUTABLE=/usr/bin/python2 \
    -D PYTHON3_EXECUTABLE=/usr/bin/python3 \
    -d PYTHON_LIBRARIES=/usr/lib/aarch64-linux-gnu/libpython3.8.so \
    -D PYTHON3_INCLUDE_DIR=/usr/include/python3.8/ \
    -D PYTHON3_INCLUDE_DIR2=/usr/include/aarch64-linux-gnu/python3.8 \
    -D PYTHON3_PACKAGES_PATH=/usr/lib/python3/dist-packages/ \
    .. && \
    ninja -j"$(nproc)" && \
    ninja install && \
    ldconfig

## ** CHATGPT SECTION END **

# Install pip and python (Python3.10 for Ubuntu22.04)
# RUN apt-get install -y python3-pip

# install opencv dependencies
RUN apt-get install ffmpeg libsm6 libxext6  -y

# copy over the requirements first to avoid cache busts from later layers
COPY scripts/Accessories/xatr/vision-pipeline/requirements.txt requirements.txt

# install python dependencies
RUN pip install -r requirements.txt
RUN pip install scikit-video

# copy the vision pipeline files
COPY scripts/Accessories/xatr/vision-pipeline vision-pipeline

# copy in the test video
COPY scripts/Accessories/xatr/cellphone.avi vision-pipeline/cellphone.avi

# copy the commons folder
COPY commons/ vision-pipeline/commons/

## ABOVE

# XATR isn't being used yet. Leave the following stuff out for now

# copy the XATR stuff
COPY XATR /opt/XATR

# set XATR environment variables
RUN export PATH="$PATH:/opt/XATR"
RUN export LD_LIBRARY_PATH="/opt/XATR/LIB"
RUN export XATR_ROOT="/opt/XATR"


# No installer currently exists for Linux. To install:
# • Copy the MATS-ATR folder to the desired installation location.
# • The path to the bin folder located in the MATS-ATR folder should be added to the
# PATH environment variable.
# • The path to the lib folder located in the MATS-ATR folder should be added to the
# LD LIBRARY PATH environment variable.
# • An XATR ROOT environment variable should be created and set to the location of
# the MATS-ATR folder.