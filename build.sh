#!/bin/bash


# === Upgrade pip to the latest version ===
pip install --upgrade pip


# === Install dependencies ===
echo "📦 Installing requirements..."
pip install -r requirements.txt


# === Apply database migrations ===
echo "🛠️ Applying migrations..."
python manage.py migrate --noinput


# === Collect static files ===
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput


# === Confirm Debug settings ===
echo "⚙️ DEBUG setting:"
python manage.py shell -c "from django.conf import settings; print(settings.DEBUG)"


echo "✅ Done! Deployed and running."