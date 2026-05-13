#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="f2b-manager"
TAG="${1:-latest}"

if [[ -z "${DOCKER_USER:-}" ]]; then
  read -rp "Docker Hub username: " DOCKER_USER
fi
FULL_IMAGE="${DOCKER_USER}/${IMAGE_NAME}:${TAG}"

echo ""
echo "==> Build: ${FULL_IMAGE}"
docker build -t "${FULL_IMAGE}" .

if [[ "$TAG" != "latest" ]]; then
  docker tag "${FULL_IMAGE}" "${DOCKER_USER}/${IMAGE_NAME}:latest"
fi

echo ""
echo "==> Login Docker Hub"
docker login

echo ""
echo "==> Push: ${FULL_IMAGE}"
docker push "${FULL_IMAGE}"

if [[ "$TAG" != "latest" ]]; then
  echo "==> Push: ${DOCKER_USER}/${IMAGE_NAME}:latest"
  docker push "${DOCKER_USER}/${IMAGE_NAME}:latest"
fi

echo ""
echo "✓ Fatto! Immagine disponibile su:"
echo "  https://hub.docker.com/r/${DOCKER_USER}/${IMAGE_NAME}"
echo ""
echo "Per deployare:"
echo "  docker run -d --name f2b-manager-web \\"
echo "    -p 8080:8080 \\"
echo "    -e F2B_API_KEY=your-secret-key \\"
echo "    -v /var/run/fail2ban:/var/run/fail2ban \\"
echo "    -v /var/lib/fail2ban:/var/lib/fail2ban:ro \\"
echo "    -v /var/log/fail2ban.log:/var/log/fail2ban.log:ro \\"
echo "    ${FULL_IMAGE}"
