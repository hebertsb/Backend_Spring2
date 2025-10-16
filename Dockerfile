FROM python:3.11-slim

# Evitar prompts y actualizar base
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema (incluye cliente postgres)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       postgresql-client \
       gcc \
       git \
    && rm -rf /var/lib/apt/lists/*

# Directorio de la aplicación
WORKDIR /app

# Copiar requirements y instalarlas
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el código
COPY . /app

# Exponer puerto (Railway usa 8080 por defecto para Gunicorn)
ENV PORT=8080
EXPOSE 8080

# Comando por defecto para arrancar gunicorn (puedes redefinir en Railway)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "1"]
