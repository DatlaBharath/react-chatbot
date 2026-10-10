#!/usr/bin/env bash
# Runs on the EC2 runner. Builds /opt/chatbot/.env at run time, replaces the running stack
# with IMAGE_TAG (MySQL data kept), then removes leftovers from previous deployments.
#
# Required env: ECR_REGISTRY IMAGE_TAG SECRET_NAME   (AWS_REGION defaults to ap-south-1)
# Credentials come from the instance IAM role.
set -euo pipefail

AWS_REGION=${AWS_REGION:-ap-south-1}
APP_DIR=/opt/chatbot
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${ECR_REGISTRY:?}" "${IMAGE_TAG:?}" "${SECRET_NAME:?}"

cp "$SRC_DIR/docker-compose.yml" "$APP_DIR/docker-compose.yml"

# .env = committed non-secret vars + secrets from Secrets Manager + build metadata
umask 077
{
  cat "$SRC_DIR/env/prod.env"
  echo
  aws secretsmanager get-secret-value --region "$AWS_REGION" --secret-id "$SECRET_NAME" \
    --query SecretString --output text | jq -r 'to_entries[] | "\(.key)=\(.value)"'
  echo "ECR_REGISTRY=$ECR_REGISTRY"
  echo "IMAGE_TAG=$IMAGE_TAG"
} > "$APP_DIR/.env.new"
mv "$APP_DIR/.env.new" "$APP_DIR/.env"

cd "$APP_DIR"
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY"

docker compose pull backend frontend
docker compose up -d --remove-orphans

# Wait for the new containers to respond before cleaning up
for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8000/api/health >/dev/null && curl -fsS http://127.0.0.1/ >/dev/null; then
    echo "healthy"
    # Cleanup of previous deployments (volumes untouched => MySQL data survives)
    docker container prune -f
    docker image prune -af
    docker builder prune -af
    exit 0
  fi
  sleep 3
done

echo "deployment failed health check" >&2
docker compose logs --tail=100 >&2
exit 1
