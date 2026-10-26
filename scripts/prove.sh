#!/bin/bash
# Bring the lab up, prove the leak, prove the fix, and remove the containers.
set -euo pipefail
cd "$(dirname "$0")/.."

cleanup() {
  docker compose down -v
}
trap cleanup EXIT

docker compose up -d --build --wait
python3 -m unittest tests/test_wrap.py
python3 poc/prove.py

LAB_MODE=safe docker compose up -d --force-recreate --no-deps --wait app
python3 poc/prove.py --expect-safe
