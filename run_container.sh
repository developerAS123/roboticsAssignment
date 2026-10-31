#!/usr/bin/env bash
set -e

# Project root directory on Fedora host
WORKSPACE_DIR="/home/ankitsingh/internAssignment"
IMAGE_NAME="${CONTAINER_IMAGE:-localhost/intern-robotics:turtlebot3}"

# Enable local container connections to Xwayland
xhost +local: >/dev/null 2>&1 || true

# Direct Rendering Infrastructure: mount AMD DRI devices to avoid NVIDIA driver null conflicts
DRI_ARGS=()
if [ -e /dev/dri/renderD128 ]; then
    DRI_ARGS+=(--device /dev/dri/renderD128)
fi
if [ -e /dev/dri/card1 ]; then
    DRI_ARGS+=(--device /dev/dri/card1)
elif [ -d /dev/dri ]; then
    DRI_ARGS+=(--device /dev/dri)
fi

# Execute container with rootless Podman
exec podman run -it --rm \
    --name intern_robotics_sim \
    --hostname ros2-sim \
    --security-opt label=disable \
    --net=host \
    --ipc=host \
    -e DISPLAY="${DISPLAY:-:0}" \
    -e QT_X11_NO_MITSHM=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
    -v "${WORKSPACE_DIR}":/workspace:z \
    -w /workspace \
    "${DRI_ARGS[@]}" \
    "${IMAGE_NAME}" \
    "$@"
