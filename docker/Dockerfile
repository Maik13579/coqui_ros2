ARG BASE_IMAGE
FROM ${BASE_IMAGE}

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

# Copy package.xml files to trigger dependency installation
COPY coqui_tts_ros2_interfaces/package.xml ${ROS_WS}/src/coqui_tts_ros2_interfaces/package.xml
#COPY coqui_tts_ros2/package.xml ${ROS_WS}/src/coqui_tts_ros2/package.xml

RUN apt update \
 && rosdep update \
 && rosdep install --from-paths ${ROS_WS}/src --ignore-src -r -y \
 && rm -rf /var/lib/apt/lists/*

# Copy source and build
COPY coqui_tts_ros2_interfaces ${ROS_WS}/src/coqui_tts_ros2_interfaces
#COPY coqui_tts_ros2 ${ROS_WS}/src/coqui_tts_ros2

WORKDIR ${ROS_WS}
RUN source /opt/ros/$ROS_DISTRO/setup.bash \
 && colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release