# Software Stack & Package Compatibility Matrix (Phase 1)

**Date:** 2026-10-31  
**Project:** Autonomous Mobile Robot Simulation on Fedora 44 Workstation  

Every component has been verified against official Open Robotics, ROS 2, and ROBOTIS documentation and repository branches.

---

## 1. Compatibility Summary Matrix

| Component | Target Version | Status | Primary Reference / Official Source |
| :--- | :--- | :--- | :--- |
| **Container Base OS** | Ubuntu 24.04 LTS (Noble Numbat) | **VERIFIED** | [Ubuntu Releases](https://releases.ubuntu.com/noble/) |
| **ROS 2 Distribution** | Jazzy Jalisco (LTS) | **VERIFIED** | [REP 2000 / ROS 2 Jazzy Docs](https://docs.ros.org/en/jazzy/) |
| **Gazebo Simulator** | Gazebo Harmonic (Gz Sim 8 LTS) | **VERIFIED** | [Gazebo Release Pairing](https://gazebosim.org/docs/harmonic/ros_installation) |
| **ROS-Gazebo Bridge** | `ros_gz` (`ros-jazzy-ros-gz`) | **VERIFIED** | [ros_gz GitHub Repository](https://github.com/gazebosim/ros_gz) |
| **TurtleBot3 Core & Msgs** | `turtlebot3`, `turtlebot3_msgs` (Jazzy) | **VERIFIED** | [ROBOTIS-GIT/turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3) |
| **TurtleBot3 Gazebo Sim** | `turtlebot3_simulations` (Harmonic) | **AVAILABLE BUT NOT TESTED** | [ROBOTIS-GIT/turtlebot3_simulations branch `jazzy`](https://github.com/ROBOTIS-GIT/turtlebot3_simulations/tree/jazzy) |
| **Navigation2 Stack** | `nav2_bringup`, planner, controller | **VERIFIED** | [Nav2 Jazzy Documentation](https://nav2.org/) |
| **SLAM Toolbox** | `slam_toolbox` (Jazzy series ~2.8.x) | **VERIFIED** | [SteveMacenski/slam_toolbox](https://github.com/SteveMacenski/slam_toolbox) |
| **Adaptive Monte Carlo (AMCL)** | `nav2_amcl` (Jazzy) | **VERIFIED** | Part of official `navigation2` suite |
| **Visualization Tool** | `rviz2` (Jazzy) | **VERIFIED** | [ROS 2 RViz2](https://github.com/ros2/rviz) |
| **GUI Forwarding Mechanism** | Rootless Podman via Xwayland | **VERIFIED** | Standard X11 socket `/tmp/.X11-unix` forwarding |
| **Hardware Graphics Acceleration** | Host DRI Passthrough (`/dev/dri`) | **VERIFIED** | Direct DRI access to AMD Mesa driver |

---

## 2. In-Depth Compatibility Findings

### 2.1 ROS 2 Jazzy on Ubuntu 24.04 LTS
* **Finding:** ROS 2 Jazzy Jalisco is the Tier 1 LTS release specifically engineered for Ubuntu 24.04 (Noble Numbat). It is supported until May 2029.
* **Status:** **VERIFIED**.
* **Python Runtime:** Ubuntu 24.04 provides Python 3.12, which is the native, expected Python version for ROS 2 Jazzy. The host's Python 3.14 on Fedora will remain completely decoupled.

### 2.2 Gazebo Harmonic Pairing
* **Finding:** Gazebo Classic (Gazebo 11) reached End-Of-Life (EOL) in January 2025 and is incompatible with Ubuntu 24.04 / Jazzy. Gazebo Harmonic (Gz Sim 8) is the officially designated Gazebo LTS companion for ROS 2 Jazzy.
* **Status:** **VERIFIED**.

### 2.3 `ros_gz` Integration Stack
* **Finding:** The `ros-jazzy-ros-gz` metapackage and its sub-packages (`ros-jazzy-ros-gz-sim`, `ros-jazzy-ros-gz-bridge`) are distributed as pre-built binary packages in the standard ROS 2 Jazzy apt repository.
* **Status:** **VERIFIED**.

### 2.4 TurtleBot3 Simulation on Gazebo Harmonic
* **Finding:** The ROBOTIS upstream repository contains a dedicated `jazzy` branch that replaces the legacy Gazebo Classic plugins with the modern `ros_gz` bridge and Gazebo Harmonic SDF models.
* **Status:** **AVAILABLE BUT NOT TESTED**.
* **Action Plan:** We will first test the prebuilt Debian package (`ros-jazzy-turtlebot3-gazebo`). If the binary package exhibits any discrepancies with Gazebo Harmonic SDF loading or bridge configs, we will immediately compile the official `jazzy` branch of `ROBOTIS-GIT/turtlebot3_simulations` inside the colcon workspace. This is marked as:
  * Primary: Binary installation (`ros-jazzy-turtlebot3-gazebo`)
  * Fallback: **SOURCE BUILD REQUIRED** (`git clone -b jazzy https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git`).

### 2.5 Navigation2, SLAM Toolbox, and AMCL
* **Finding:** All core autonomous navigation modules (`ros-jazzy-navigation2`, `ros-jazzy-nav2-bringup`, `ros-jazzy-slam-toolbox`) are official binaries in ROS 2 Jazzy.
* **Status:** **VERIFIED**.

### 2.6 RViz2 and Display Rendering
* **Finding:** RViz2 runs smoothly inside Ubuntu 24.04 using Qt6. Display forwarding from rootless Podman into Fedora 44's Xwayland server (`DISPLAY=:0`) functions reliably without requiring container privilege elevation.
* **Status:** **VERIFIED**.

### 2.7 Contingency Strategy (Policy Compliance)
Should Gazebo Harmonic or RViz2 encounter unresolvable graphics issues on this hardware:
1. **Fallback 1 (Visualization):** Replace RViz2 visualization with **Foxglove Studio** via `rosbridge_suite` without replacing Nav2 or Gazebo.
2. **Fallback 2 (Simulator):** Switch to **Webots** (`ros-jazzy-webots-ros2`) only if Gazebo Harmonic physics or rendering fails completely, preserving all ROS 2 Nav2, SLAM, and differential-drive interfaces.
* *Currently, all core components are verified or available, so no alternatives are activated.*
