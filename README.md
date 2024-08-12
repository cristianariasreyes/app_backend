# agora_backend

python: 3.12.2
postgres: 16.3

1.- Crear entorno de desarrollo: python3 -m venv venv
2.- Activar entorno: source venv/bin/activate
3.- Instalar requirements: pip install -r requirements.txt

Primera vez:
- python manage.py createsuperuser
- python manage.py makemigrations
- python manage.py migrate

Correr proyecto: python manage.py runserver

 python manage.py makemigrations --settings=autopractik.settings.local
 python manage.py migrate --settings=autopractik.settings.local


## Docker image

- build a new version: docker build -t agora-backend-v1 .
- construir docker compose y levantar: docker-compose up --build
