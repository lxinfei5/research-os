#!/usr/bin/env bash
# ResearchOS CLI wrapper. Keeps the caller's cwd (so relative capture-payload paths resolve
# naturally) while making the `ros` package importable from anywhere. The data root is the repo
# dir regardless of cwd (ros/paths.py derives it from __file__; override with ROS_ROOT).
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec env PYTHONPATH="${DIR}${PYTHONPATH:+:${PYTHONPATH}}" python3 -m ros "$@"
