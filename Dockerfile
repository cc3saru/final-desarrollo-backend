# Usa una imagen oficial de Python como base
FROM python:3.10

# Configura el entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Configura el directorio de trabajo
WORKDIR /code

# Instala las dependencias
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia el proyecto
COPY . /code/

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Ejecuta el servidor de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
