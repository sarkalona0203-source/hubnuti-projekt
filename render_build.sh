#!/bin/bash
set -e

# --- 1) Фронтенд ---
cd frontend
npm install
npm run build

# --- 2) Бэкенд ---
cd ../backend
pip install -r requirements.txt
python manage.py collectstatic --noinput