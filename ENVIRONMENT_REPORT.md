# Environment Inspection Report (Phase 0)

**Date:** 2026-10-31  
**Target:** Robotics Software Internship Autonomous Mobile Robot Project  
**Status:** COMPLETE — System Inspected and Safe for Execution  

---

## 1. Host System Specifications

| Component | Specification | Operational Status |
| :--- | :--- | :--- |
| **Operating System** | Fedora Linux 44 (Workstation Edition) | Verified (Kernel 7.2.13-200.fc44.x86_64) |
| **CPU Architecture** | AMD Ryzen 5 5600H with Radeon Graphics | Verified (6 Physical Cores, 12 Threads) |
| **System Memory** | 7.1 GiB Physical RAM | 5.0 GiB Used, ~2.1 GiB Available |
| **Swap Space** | 20.0 GiB Swap | 1.5 GiB Used, 18.5 GiB Free |
| **Storage Capacity** | NVMe SSD (`/dev/nvme0n1p4`) | 461 GiB total, **321 GiB free** on `/home` |
| **Host Python** | Python 3.14 (Fedora 44 standard) | **Isolated** (Will NOT be exposed to container) |
| **Container Engine** | Podman 5.8.9 (Rootless) | Verified (`ankitsingh:524288:65536` subuid/subgid) |
| **Display Server** | Wayland (GNOME Shell 48/Xwayland) | Active (`WAYLAND_DISPLAY=wayland-0`, `DISPLAY=:0`) |
| **Discrete GPU** | NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM) | Active (NVIDIA Driver 615.78.08, CUDA 13.4) |
| **Integrated GPU** | AMD Radeon Cezanne Graphics | Active (`/dev/dri/card1`, `/dev/dri/renderD128`) |

---

## 2. Display and GUI Forwarding Analysis

* **Display Server Setup:** The host runs a standard GNOME Wayland compositor. Xwayland is active as a daemon (`DISPLAY=:0`, PID 5543) listening on `/tmp/.X11-unix/X0`.
* **Access Control:** `xhost` is installed on Fedora (`/usr/bin/xhost`). Running `xhost +local:` or `xhost +si:localuser:ankitsingh` provides container access to Xwayland without compromising network security.
* **Rendering Strategy:**
  1. Gazebo Harmonic and RViz2 utilize Qt and OpenGL/Vulkan.
  2. While native Wayland forwarding inside containers can suffer from unstable client-side decorations or Qt platform plugin crashes, forwarding via **Xwayland (`DISPLAY=:0`, `/tmp/.X11-unix`)** provides guaranteed stability and broad compatibility across Gazebo Sim and RViz2.

---

## 3. GPU and Acceleration Analysis

* **NVIDIA GPU:** The RTX 3050 Laptop GPU is functioning with driver `615.78.08`. However, `nvidia-container-toolkit` (`nvidia-ctk`) is not installed on the host. Per the project safety rules, **we will not modify or reinstall host NVIDIA drivers**.
* **AMD Hardware Acceleration:** The host has direct DRI nodes (`/dev/dri/card1`, `/dev/dri/renderD128`) for the AMD Ryzen 5600H integrated graphics. Mounting `/dev/dri` into the container provides native Mesa VA-API and OpenGL/Vulkan acceleration without host driver tampering or proprietary library mismatches.
* **Mesa Software Fallback:** Mesa `llvmpipe` (`LIBGL_ALWAYS_SOFTWARE=1`) is available if hardware DRI surfaces encounter context errors, guaranteeing rendering will never hard-block the simulation.

---

## 4. Memory Footprint and System Safety Plan

With 7.1 GiB physical RAM and ~2.1 GiB available, running a combined simulation (Gazebo GUI + RViz2 + Nav2 + SLAM Toolbox) must be carefully managed to avoid memory thrashing:

1. **Lightweight Environment:** We will avoid heavy multi-room meshes and use standard low-polygon indoor worlds (`turtlebot3_world.sdf` or minimal room).
2. **Lean RViz2 Profile:** Use a minimal RViz2 configuration displaying only essential topics (`/scan`, `/map`, `/plan`, `/tf`, and robot model), avoiding pointclouds or high-frequency rendering.
3. **Gazebo Resource Optimization:** Gazebo Harmonic physics can run at standard 250 Hz step size with GUI update rate throttled to 30 Hz. When performing extensive mapping or long navigation runs, Gazebo can also run headless (`gz sim -s -r`) while RViz2 handles visualization.
4. **Swap Buffer:** The 20 GiB swap ensures that the Linux kernel OOM-killer will not terminate tasks abruptly during transient memory spikes. Memory usage will be monitored continuously using `free -h` and `vmstat`.
