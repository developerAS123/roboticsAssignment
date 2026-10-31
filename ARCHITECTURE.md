# System & Software Architecture Design

**Project:** Autonomous Mobile Robot Simulation  
**Platform:** Fedora 44 Workstation + Rootless Podman Container  

---

## 1. System Layer Diagram

```
+---------------------------------------------------------------------------------+
| FEDORA 44 WORKSTATION HOST                                                      |
|                                                                                 |
| - Kernel: Linux 7.2.13-200.fc44.x86_64                                          |
| - Desktop: GNOME Wayland + Xwayland (DISPLAY=:0)                                |
| - Hardware: AMD Ryzen 5 5600H (12 threads) | 7.1 GB RAM + 20 GB Swap            |
| - Graphics: AMD Radeon Cezanne iGPU (/dev/dri) & RTX 3050 (Driver 615.78.08)    |
| - Persistent Storage: ~/internAssignment/ (321 GB free space)                  |
+---------------------------------------------------------------------------------+
                                      |
         Rootless Podman Bind Mount & Display Sockets Forwarding
         -v /home/ankitsingh/internAssignment:/workspace:z
         -v /tmp/.X11-unix:/tmp/.X11-unix:ro
         --device /dev/dri
                                      v
+---------------------------------------------------------------------------------+
| UBUNTU 24.04 LTS PODMAN CONTAINER (Rootless)                                    |
|                                                                                 |
| Python 3.12 (Isolated from host Python 3.14)                                    |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| | ROS 2 JAZZY JALISCO (Base Environment)                                      | |
| |                                                                             | |
| |  [ Gazebo Harmonic ] <---- ros_gz_bridge ----> [ ROS 2 Core Topics ]        | |
| |  - World: indoor_world.sdf                      - /scan (sensor_msgs/Laser) | |
| |  - Robot: TurtleBot3 Burger                     - /odom (nav_msgs/Odometry) | |
| |  - Diff-Drive & LiDAR Plugins                   - /cmd_vel (geometry_msgs)  | |
| |                                                 - /tf, /tf_static           | |
| +-----------------------------------------------------------------------------+ |
|                                       |                                         |
|                                       v                                         |
| +-----------------------------------------------------------------------------+ |
| | AUTONOMOUS NAVIGATION STACK (Navigation2 & SLAM)                            | |
| |                                                                             | |
| |  - Mapping: SLAM Toolbox (online asynchronous SLAM -> map generation)       | |
| |  - Localization: AMCL (Monte Carlo particle filter localization)            | |
| |  - Global Planning: Navfn / Costmap 2D (global costmap)                     | |
| |  - Local Planning: DWB / Regulated Pure Pursuit (local costmap + avoidance) | |
| |  - Recovery Behaviors: Spin, backup, wait                                   | |
| |  - Lifecycle Manager: Manages Nav2 system states                            | |
| +-----------------------------------------------------------------------------+ |
|                                       |                                         |
|                                       v                                         |
| +-----------------------------------------------------------------------------+ |
| | APPLICATION & VISUALIZATION LAYER                                           | |
| |                                                                             | |
| |  - Python Navigation Client: Action client calling NavigateToPose           | |
| |  - RViz2: Visualizes robot model, TF trees, costmaps, laser scans & goals   | |
| +-----------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------+
```

---

## 2. Topic & Data Flow Architecture

```
  +-------------------------+
  | Gazebo Harmonic (Sim)   |
  +-------------------------+
       |             ^
(GZ Transport)       | (GZ Transport)
       |             |
       v             |
  +-------------------------+
  |      ros_gz_bridge      |
  +-------------------------+
       | /scan       | /cmd_vel
       | /odom       ^
       v             |
  +-------------------------+
  |    Nav2 / Controller    | <====== [ Python Navigation Client ]
  +-------------------------+          (Sends NavigateToPose goal)
       |             ^
       | /tf         | /plan
       v             v
  +-------------------------+
  |          RViz2          |
  +-------------------------+
```

---

## 3. Directory Layout on Host (`~/internAssignment`)

The host directory is mounted directly to `/workspace` inside the container:

```
~/internAssignment/
├── ENVIRONMENT_REPORT.md       # Phase 0 diagnostic report
├── PACKAGE_COMPATIBILITY.md    # Phase 1 software compatibility matrix
├── ARCHITECTURE.md             # System architecture and design specification
├── IMPLEMENTATION_STATUS.md    # Phase-by-phase implementation progress tracker
├── Containerfile               # Container build definition for Ubuntu 24.04 + ROS 2
├── compose.yaml                # Optional Podman compose definition
├── colcon_ws/                  # Persistent ROS 2 workspace
│   ├── src/                    # Source packages and launch files
│   ├── build/                  # Build artifacts
│   └── install/                # Installed binaries and setup hooks
├── worlds/                     # Gazebo simulation worlds (.sdf)
├── maps/                       # Saved occupancy grid maps (.yaml, .pgm)
├── config/                     # Nav2, SLAM Toolbox, and RViz configuration files
├── launch/                     # Unified bringup launch files
├── scripts/                    # Python navigation action client and automation scripts
├── robot/                      # Robot description (URDF/SDF models, meshes)
└── docs/                       # Project documentation, evidence, and video instructions
```

---

## 4. Hardware Resource Budget

| Subsystem | Estimated RAM Usage | Estimated CPU Allocation | GPU VRAM Allocation |
| :--- | :--- | :--- | :--- |
| Ubuntu Base & Python | 150 MB | < 0.2 Cores | 0 MB |
| Gazebo Harmonic Physics | 400 MB | 1.0 – 1.5 Cores | ~100 MB |
| Gazebo GUI (if enabled) | 450 MB | 0.5 Cores | ~250 MB |
| ROS 2 Core & ros_gz_bridge | 180 MB | 0.3 Cores | 0 MB |
| Navigation2 Stack + AMCL | 550 MB | 1.0 – 1.5 Cores | 0 MB |
| SLAM Toolbox (during mapping)| 350 MB | 0.8 Cores | 0 MB |
| RViz2 Visualization | 300 MB | 0.4 Cores | ~200 MB |
| **Total Estimated Peak** | **~2.3 – 2.4 GB** | **~3.5 – 4.5 Cores** | **~550 MB** |

*Evaluation:* The estimated peak footprint (~2.3 GB RAM) matches the currently available 2.1 GB physical RAM plus 18.5 GB active swap. Performance will remain responsive on the 6-core / 12-thread AMD Ryzen 5 5600H.
