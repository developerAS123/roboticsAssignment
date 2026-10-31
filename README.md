# Autonomous Mobile Robot Simulation (Intern Assignment)

## Overview
This repository contains a **complete, reproducible ROS 2 Jazzy simulation** of a TurtleBot3 Burger navigating an indoor environment with SLAM, localization, and Nav2 navigation. The project demonstrates:
- Differential‑drive robot simulation in Gazebo Harmonic (via `ros_gz` bridge).
- 2‑D laser scan and odometry publishing.
- Online SLAM (SLAM Toolbox) to generate a map.
- AMCL localization on the generated map.
- Nav2 navigation with obstacle avoidance (static box obstacle).
- A Python client that can send one or many navigation goals.
- Automated end‑to‑end testing script.

All steps run **inside a root‑less Podman container** based on Ubuntu 24.04, keeping the host Fedora 44 system untouched.

---

## Repository Structure
```
internAssignment/
├── config/                     # Parameter files
│   ├── nav2_params.yaml        # Nav2 configuration (AMCL, planner, controller, …)
│   └── slam_params.yaml        # SLAM Toolbox parameters (optional override)
├── launch/                     # ROS2 launch files
│   ├── tb3_sim.launch.py       # TurtleBot3 simulation (headless / GUI)
│   ├── tb3_slam2.launch.py     # SLAM launch (online_async) – reference
│   ├── tb3_nav2.launch.py      # Full Nav2 stack (simulation + navigation)
│   └── tb3_slam.launch.py      # Legacy map‑generation launch (kept for reference)
├── worlds/                     # Gazebo world files
│   ├── indoor_world.sdf        # Original empty indoor world
│   └── indoor_world_obstacle.sdf # Same world with a red box obstacle
├── maps/                       # Generated map (added after SLAM run)
│   ├── office_map.yaml
│   └── office_map.pgm
├── scripts/                    # Helper scripts & Python nodes
│   ├── run_slam_generate_map.sh # Simple SLAM‑map generation script (legacy)
│   ├── navigate_multi_goal.py   # Multi‑goal Python client
│   └── run_full_test.sh        # Automated end‑to‑end test (SLAM → Nav2 → goals)
├── docs/                       # Documentation, screenshots, video checklist
│   └── README_assets.md        # Placeholder for assets (images, video link)
├── .gitignore                  # Files/folders to ignore in git
└── README.md                  # **You are reading it!**
```

---

## Prerequisites (Host – Fedora 44)
1. **Podman** (already installed).
2. A **GPU** with drivers (NVIDIA 615 driver is installed; the simulation runs head‑less, so GPU is optional).
3. **Git** for version control.
4. Optionally, **FFmpeg** for recording the demo video.

---

## Setup – Build the Container
```bash
# Clone the repository (once you push it – see "Publishing" below)
# cd ~
# git clone <your‑repo‑url>
# cd internAssignment

# Build the base image (only needed the first time)
podman build -t localhost/intern-robotics:base -f Dockerfile.base .

# Build the ROS‑Jazzy image (includes ROS2, Gazebo, Nav2, etc.)
podman build -t localhost/intern-robotics:ros2-jazzy -f Dockerfile.ros .
```
*(Dockerfiles are already present in the repo – they were created in earlier phases.)*

---

## Running the Simulation
```bash
# Start a persistent container with the workspace mounted
podman run -it --rm \
  --name intern_robotics_sim \
  --security-opt label=disable \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v $HOME/internAssignment:/workspace:z \
  -w /workspace \
  localhost/intern-robotics:ros2-jazzy \
  bash
```
Inside the container, you can execute the helper scripts, e.g.:
```bash
# 1️⃣ Generate a map (25 s SLAM run)
./scripts/run_slam_generate_map.sh

# 2️⃣ Launch Nav2 with the obstacle world
ros2 launch launch/tb3_nav2.launch.py world:=/workspace/worlds/indoor_world_obstacle.sdf headless:=true use_sim_time:=true

# 3️⃣ Send navigation goals (single or multiple)
./scripts/navigate_multi_goal.py 1.0 0.0 0.0 -0.5 0.5 1.57
```
---

## Automated Testing
Run the full end‑to‑end test (SLAM → Nav2 → three goals) with a single command:
```bash
./scripts/run_full_test.sh
```
The script prints a concise summary and exits with status 0 on success.

---

## Recording the Demonstration Video
A short 1‑2 minute video should show:
1. Gazebo window (or headless rendering captured via `ffmpeg` + `screen` utilities).
2. RViz2 visualising the map, laser scan, robot pose, and planned path.
3. Setting a navigation goal and the robot autonomously reaching it while avoiding the red obstacle.

**Suggested command** (run on the host, not inside the container):
```bash
ffmpeg -f x11grab -video_size 1280x720 -i $DISPLAY -t 120 -c:v libx264 -preset fast demo.mp4
```
Add the resulting `demo.mp4` to the repository (under `docs/`), and update the *Video* section of this README with the link.

---

## Publishing (GitHub)
1. **Create a new repository** on GitHub (e.g., `username/robotics‑intern‑assignment`).
2. On your workstation, run:
```bash
cd $HOME/internAssignment
git init
git remote add origin https://github.com/<your‑username>/robotics-intern-assignment.git
git add .
git commit -m "Initial commit – full ROS2 simulation pipeline"
git push -u origin master
```
3. Enable **GitHub Pages** (optional) to host the documentation.

---

## License
This educational material is released under the **MIT License**. See the `LICENSE` file for details.

---

## Acknowledgements
- ROS 2 Jazzy, Gazebo Harmonic, SLAM Toolbox, Nav2 – Open Source Robotics Foundation.
- TurtleBot3 simulation packages – Robotis.
- Antigravity (AGY) tooling – Google DeepMind.

---

*Happy hacking, and good luck with your robotics internship assignment!*
