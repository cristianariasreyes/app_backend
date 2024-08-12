# Usa una imagen base de Python 3.12.2
FROM python:3.12.2-slim

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para pyodbc
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    unixodbc \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia env
COPY .env .

# Copia el archivo de requerimientos al contenedor
COPY ./requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el archivo .env al contenedor desde el directorio agora_project
COPY . .

# Copia el código fuente del proyecto al contenedor
# COPY backend/ /app/backend/

# Copia los archivos de frontend al contenedor
# COPY frontend/ /app/frontend/

# Exponer el puerto en el que corre la aplicación Django
EXPOSE 8000

# Comando para ejecutar la aplicación Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
