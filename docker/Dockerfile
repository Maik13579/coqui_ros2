ARG BASE_IMAGE=ros:humble
FROM ${BASE_IMAGE}

# Environment variables
ENV ROS_WS=/root/ros2_ws
ENV DEBIAN_FRONTEND=noninteractive
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Use bash
SHELL ["/bin/bash", "-c"]

# Source ROS entrypoint
COPY docker/ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh
ENTRYPOINT ["/ros_entrypoint.sh"]

# Install Dependencies
RUN apt update \
 && apt install -y \
 ros-$ROS_DISTRO-rmw-cyclonedds-cpp \
 python3 python3-pip python3-dev python3-venv python3-wheel build-essential \
 gcc g++ make espeak-ng libsndfile1-dev \
 && rm -rf /var/lib/apt/lists/*
RUN pip3 install llvmlite --ignore-installed
RUN pip3 install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

# Install TTS
COPY TTS /root/TTS
WORKDIR /root/TTS
RUN make install