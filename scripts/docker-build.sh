#!/usr/bin/env sh
set -e

root=$(cd "$(dirname "$0")/.." && pwd)
image="${CUSTOMER_API_IMAGE:-ghcr.io/mentor-forge/mentorhub_customer_api:latest}"
exec docker build --build-arg "BUILT_AT=${BUILT_AT:-LOCAL}" -t "$image" -f "$root/Dockerfile" "$root"
