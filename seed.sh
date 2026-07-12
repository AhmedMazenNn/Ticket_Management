#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/backend"

echo "=== Running migrations ==="
source .venv/bin/activate
python manage.py migrate --verbosity=0

echo ""
echo "=== Seeding database ==="
python manage.py seed

echo ""
echo "Done! Start the backend with: make dev-backend"
