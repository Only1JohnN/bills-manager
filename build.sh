#!/bin/bash

# Upgrade pip to the latest version
pip install --upgrade pip

# Install the necessary dependencies from requirements.txt
pip install -r requirements.txt

# Run database migrations (ensure database is up-to-date)
python manage.py migrate --noinput

# Collect static files (for production)
python manage.py collectstatic --noinput