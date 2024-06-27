FROM python:3.11-slim

WORKDIR /code

# Actualiza los paquetes existentes e instala las dependencias necesarias
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    postgresql-client \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x wait-for-it.sh

# Copia la carpeta alembic y el archivo alembic.ini 
COPY alembic alembic
COPY alembic.ini alembic.ini

CMD [ "./wait-for-it.sh", "db:5432", "--", "uvicorn" , "api.main:app", "--host", "0.0.0.0", "--reload" ]
