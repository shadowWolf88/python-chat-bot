#!/usr/bin/env bash
# Simple deploy helper: push current branch to origin and optionally deploy to Railway
set -euo pipefail

BRANCH=${1:-$(git rev-parse --abbrev-ref HEAD)}

echo "Pushing branch $BRANCH to origin..."
git push origin "$BRANCH"

if command -v railway >/dev/null 2>&1; then
  if [ -z "${RAILWAY_TOKEN-}" ] || [ -z "${RAILWAY_PROJECT-}" ]; then
    echo "RAILWAY_TOKEN or RAILWAY_PROJECT not configured. Skipping Railway deploy."
    exit 0
  fi

  echo "Deploying to Railway project $RAILWAY_PROJECT..."
  railway up --project "$RAILWAY_PROJECT" --detach
  echo "Railway deploy triggered."
else
  echo "Railway CLI not found. Install from https://railway.app/ to enable direct deploys."
fi
