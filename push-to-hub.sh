#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="f2b-manager"
DOCKER_USER="${DOCKER_USER:-slashino}"
TAG="${1:-latest}"
PLATFORMS="${PLATFORMS:-linux/amd64,linux/arm64}"
BUILDER="f2b-multiarch"

FULL_IMAGE="${DOCKER_USER}/${IMAGE_NAME}:${TAG}"

echo ""
echo "==> Immagine : ${FULL_IMAGE}"
echo "==> Piattaforme: ${PLATFORMS}"
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
echo "==> Build & push multi-arch"
docker buildx build \
  --platform "${PLATFORMS}" \
  --tag "${FULL_IMAGE}" \
  $( [[ "${TAG}" != "latest" ]] && echo "--tag ${DOCKER_USER}/${IMAGE_NAME}:latest" ) \
  --push \
  .

echo ""
echo "✓ Fatto! Manifest multi-arch disponibile su:"
echo "  https://hub.docker.com/r/${DOCKER_USER}/${IMAGE_NAME}"
echo ""
echo "  amd64 e arm64 vengono scelti automaticamente da Docker al pull."
