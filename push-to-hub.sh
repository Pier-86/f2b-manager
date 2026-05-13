#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="f2b-manager"
DOCKER_USER="${DOCKER_USER:-slashino}"
TAG="${1:-latest}"
BUILDER="f2b-multiarch"

BASE="${DOCKER_USER}/${IMAGE_NAME}"

echo ""
echo "==> Immagine : ${BASE}"
echo "==> Tag che verranno creati:"
echo "      ${BASE}:amd64"
echo "      ${BASE}:arm64"
echo "      ${BASE}:${TAG}  (manifest multi-arch)"
echo ""

echo "==> Login Docker Hub"
docker login -u "${DOCKER_USER}"

echo ""
echo "==> Configuro buildx builder (${BUILDER})"
if ! docker buildx inspect "${BUILDER}" &>/dev/null; then
  docker buildx create --name "${BUILDER}" --driver docker-container --bootstrap
fi
docker buildx use "${BUILDER}"

echo ""
echo "==> Build & push linux/amd64"
docker buildx build --platform linux/amd64 --tag "${BASE}:amd64" --push .

echo ""
echo "==> Build & push linux/arm64"
docker buildx build --platform linux/arm64 --tag "${BASE}:arm64" --push .

echo ""
echo "==> Creo manifest multi-arch :${TAG}"
docker buildx imagetools create \
  --tag "${BASE}:${TAG}" \
  "${BASE}:amd64" \
  "${BASE}:arm64"

echo ""
echo "✓ Fatto! Disponibile su: https://hub.docker.com/r/${BASE}"
echo ""
echo "  Usa il tag corretto per il tuo server:"
echo "    amd64  →  ${BASE}:amd64"
echo "    arm64  →  ${BASE}:arm64"
echo "    auto   →  ${BASE}:${TAG}"
