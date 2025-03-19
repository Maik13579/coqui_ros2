ARG BASE_IMAGE=text_to_suppress_warning #used for later stages

ARG UBUNTU_MAJOR=22
ARG UBUNTU_MINOR=04
ARG CUDA_MAJOR=12
ARG CUDA_MINOR=6
ARG CUDA_PATCH=3
ARG ROS_DISTRO=humble
ARG BASE=nvidia/cuda:${CUDA_MAJOR}.${CUDA_MINOR}.${CUDA_PATCH}-base-ubuntu${UBUNTU_MAJOR}.${UBUNTU_MINOR}
FROM ${BASE} as base
ARG ROS_DISTRO
ENV ROS_DISTRO=$ROS_DISTRO
ENV DEBIAN_FRONTEND=noninteractive
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ENV ROS_WS=/root/ros2_ws

# Install locales, curl, gnupg, and lsb-release
RUN apt-get update && apt-get install -y \
    locales \
    curl \
    gnupg2 \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Set locale to UTF-8
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# Add ROS 2 repository key and source list
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -sc) main" \
    > /etc/apt/sources.list.d/ros2-latest.list

# Install ROS2 Desktop and additional dependencies
RUN apt-get update && apt-get install -y \
    ros-$ROS_DISTRO-desktop \
    ros-$ROS_DISTRO-rmw-cyclonedds-cpp \
    python3-rosdep \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep
RUN rosdep init && rosdep update
COPY docker/ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh
ENTRYPOINT ["/ros_entrypoint.sh"]

# Setup environment to source ROS2
SHELL ["/bin/bash", "-c"]
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> ~/.bashrc
CMD ["bash"]



# Build TTS
FROM ${BASE_IMAGE} as build_tts

# Install Dependencies
RUN apt update \
 && apt install -y \
 ros-$ROS_DISTRO-rmw-cyclonedds-cpp \
 python3 python3-pip python3-dev python3-venv python3-wheel build-essential \
 gcc g++ make espeak-ng libsndfile1-dev alsa-utils \
 && rm -rf /var/lib/apt/lists/*
RUN pip3 install llvmlite --ignore-installed
RUN pip3 install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

# Install TTS
COPY TTS /root/TTS
WORKDIR /root/TTS
RUN make install



# This stages downloands some models into the image
FROM ${BASE_IMAGE} as download_models
COPY TTS /root/TTS
COPY scripts /scripts
#RUN python3 /scripts/clone_model.py tts_models/de/thorsten/tacotron2-DDC
RUN python3 /scripts/clone_model.py tts_models/en/ljspeech/glow-tts
RUN python3 /scripts/clone_model.py tts_models/multilingual/multi-dataset/xtts_v2

# Get voices for cloning
RUN apt update && apt install -y git ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /voices
RUN git clone https://github.com/renandincer/libtrump.git
# Convert all .mp3 files in /voices to .wav and remove the original .mp3 files
RUN find /voices -type f -name "*.mp3" -exec sh -c 'ffmpeg -y -i "$1" "${1%.mp3}.wav" && rm -f "$1"' _ {} \;



# Build roswrapper
FROM ${BASE_IMAGE} as build_ros

# Copy package.xml files to trigger dependency installation
COPY coqui_tts_ros2_interfaces/package.xml ${ROS_WS}/src/coqui_tts_ros2_interfaces/package.xml
COPY coqui_tts_ros2/package.xml ${ROS_WS}/src/coqui_tts_ros2/package.xml

RUN apt update \
 && rosdep update \
 && rosdep install --from-paths ${ROS_WS}/src --ignore-src -r -y \
 && rm -rf /var/lib/apt/lists/*

# Copy source and build
COPY coqui_tts_ros2_interfaces ${ROS_WS}/src/coqui_tts_ros2_interfaces
COPY coqui_tts_ros2 ${ROS_WS}/src/coqui_tts_ros2

WORKDIR ${ROS_WS}
RUN source /opt/ros/$ROS_DISTRO/setup.bash \
 && colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release