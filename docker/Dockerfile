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