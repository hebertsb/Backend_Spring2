#!/bin/bash
# Script de inicio para Railway - Ejecuta migraciones antes de iniciar el servidor

echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "🤖 Iniciando scheduler de campañas en background..."
python manage.py run_campaign_scheduler &
SCHEDULER_PID=$!
echo "✅ Scheduler iniciado con PID: $SCHEDULER_PID"

echo "🚀 Iniciando servidor Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
