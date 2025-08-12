#!/usr/bin/env bash
# exit on error
set -o errexit

npm install
npm run build

pip install -r requirements.txt

python -c "from src.app import app; from src.api.models import db; app.app_context().push(); db.create_all()"
