# Containerfile for Ubuntu 24.04 ROS 2 & Gazebo Environment
FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install base utilities, networking, and graphics testing packages
# Note: In Ubuntu 24.04, libegl1 and libgl1 replace deprecated transitional packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    curl \
    gnupg2 \
    lsb-release \
    sudo \
    bash-completion \
    build-essential \
    git \
    wget \
    nano \
    pciutils \
    mesa-utils \
    x11-apps \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libgl1 \
    libegl1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up locale for ROS 2 compatibility (requires UTF-8)
RUN locale-gen en_US en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Create a default non-root user matching standard host UID 1000
ARG USERNAME=robot
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME 2>/dev/null || true && \
    id -u $USERNAME >/dev/null 2>&1 || useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME && \
    usermod -aG video,render $USERNAME 2>/dev/null || true

# Set up working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]
