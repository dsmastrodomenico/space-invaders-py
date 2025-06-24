# Usa una imagen base de Python ligera
FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivo del juego al directorio de trabajo
COPY main.py /app/

# Instalar las dependencias necesarias.
# 'python3-dev' es fundamental para que el paquete 'keyboard' se compile correctamente.
# Se añade 'kbd' para proporcionar 'dumpkeys' y otras utilidades de teclado.
RUN apt-get update && apt-get install -y python3-dev kbd \
    && pip install keyboard \
    && rm -rf /var/lib/apt/lists/*

# Comando para ejecutar el juego cuando el contenedor inicie
CMD ["python", "main.py"]