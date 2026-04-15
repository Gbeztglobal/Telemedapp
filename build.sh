#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Migrate — don't fail the build if DB isn't ready yet
python manage.py migrate || echo "⚠️  Migration skipped — database not yet available. Run manually via Render Shell."
