# Usa una imagen base de Python ligera
FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia tu archivo del juego al directorio de trabajo
COPY . /app/

# Comando para ejecutar el juego cuando el contenedor inicie
CMD ["python", "main.py"]