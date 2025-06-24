Space Invaders para Terminal (Versión Simple)

Este es un juego básico de "Space Invaders" implementado en Python para ejecutarse directamente en la terminal. Esta versión está diseñada para ser simple y didáctica, utilizando únicamente funciones y variables globales, sin la complejidad de las clases o módulos separados, lo que la hace ideal para entender la lógica fundamental del juego.
Características

    Movimiento del Jugador: Mueve tu nave de izquierda a derecha.

    Disparos: Dispara proyectiles para destruir a los invasores.

    Puntuación: Gana puntos por cada invasor eliminado.

    Final del Juego: El juego termina si los invasores llegan al final de la pantalla o chocan con tu nave.

    Reiniciar/Salir: Opción para reiniciar el juego o salir al finalizar la partida.

Cómo Jugar

    Iniciar el Juego: Ejecuta el script. El juego esperará a que presiones cualquier tecla para comenzar.

    Moverse: Usa las teclas de flecha izquierda y flecha derecha del teclado para mover tu nave (A).

    Disparar: Presiona la barra espaciadora para que tu nave dispare proyectiles (|).

    Objetivo: Destruye a todos los invasores (V) antes de que lleguen al final de la pantalla.

    Game Over: Si un invasor llega al borde inferior de la pantalla o colisiona con tu nave, el juego terminará.

    Reiniciar: Después de "GAME OVER", presiona la tecla R para jugar de nuevo.

    Salir: Después de "GAME OVER", presiona la tecla Q para salir del juego.

Requisitos

    Python 3.x

    La librería keyboard de Python.

Instalación y Ejecución

    Guarda el Código: Guarda todo el código proporcionado (la versión simple en un solo archivo) como main.py en tu máquina.

    Instala la Dependencia: Abre tu terminal o línea de comandos y ejecuta el siguiente comando para instalar la librería keyboard:

    pip install keyboard

    Ejecuta el Juego: Navega hasta el directorio donde guardaste main.py y ejecuta el script con Python:

    python main.py

Ejecución con Docker (Opcional)

Puedes ejecutar este juego dentro de un contenedor Docker para aislar su entorno.

    Crea el Dockerfile: En el mismo directorio donde guardaste main.py, crea un archivo llamado Dockerfile (sin extensión) con el siguiente contenido:

    # Usa una imagen base de Python
    FROM python:3.9-slim-buster

    # Establece el directorio de trabajo dentro del contenedor
    WORKDIR /app

    # Copia los archivos del juego al directorio de trabajo
    COPY . /app

    # Instala las dependencias (necesita python3-dev para compilar keyboard)
    RUN apt-get update && apt-get install -y python3-dev \
        && pip install keyboard \
        && rm -rf /var/lib/apt/lists/*

    # Comando para ejecutar el juego cuando el contenedor inicie
    CMD ["python", "main.py"]

    Construye la Imagen Docker: Desde tu terminal en el mismo directorio, ejecuta:

    docker build -t space-invaders-simple .

    Ejecuta el Contenedor: Para iniciar el juego en un contenedor interactivo:

    docker run -it space-invaders-simple

Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE (si se incluye) para más detalles.