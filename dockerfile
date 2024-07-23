# Usa una imagen base de Python 3.11.2
FROM python:3.11.2-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app/backend

# Instala las dependencias del sistema necesarias para pyodbc
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    unixodbc \
    && rm -rf /var/lib/apt/lists/*


# Copia el archivo de requerimientos al contenedor
COPY backend/requirements.txt /app/backend/

# Instala las dependencias
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copia el archivo .env al contenedor desde el directorio agora_project
COPY .env /app/

# Copia el código fuente del proyecto al contenedor
COPY backend/ /app/backend/

# Copia los archivos de frontend al contenedor
COPY frontend/ /app/frontend/

# Exponer el puerto en el que corre la aplicación Django
EXPOSE 8000

# Comando para ejecutar la aplicación Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
