#!/bin/sh
set -e  # exit if any command fails

echo "Waiting for PostgreSQL at 69.62.78.167:5432..."

until pg_isready -h "69.62.78.167" -p "5432" -U "postgres"; do
  sleep 2
done

echo "PostgreSQL is ready!"

# Apply database migrations
python manage.py makemigrations --noinput

python manage.py migrate --noinput
echo "Migrations applied!"

# Collect static files
python manage.py collectstatic --noinput
echo "Static files collected!"


# Start Gunicorn server
exec gunicorn visual_generator_tool.wsgi:application --bind 0.0.0.0:8002 --workers 3
