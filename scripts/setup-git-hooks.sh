#!/usr/bin/env bash
# Install git hooks from .githooks into .git/hooks
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(dirname "$HERE")

if [ ! -d "$REPO_ROOT/.git" ]; then
  echo "This does not look like a git repository. Run this from the project root." >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/.git/hooks"
cp -r "$REPO_ROOT/.githooks/"* "$REPO_ROOT/.git/hooks/"
chmod +x "$REPO_ROOT/.git/hooks/"*

echo "Installed git hooks to .git/hooks. To ensure hooks are used by new clones, run this script after cloning." 

exit 0
