Space Invaders para Terminal (Versión Modular)

Esta es una implementación del clásico juego "Space Invaders" para la terminal. Ha sido refactorizado para utilizar una estructura modular basada en clases y archivos separados, lo que mejora la organización, legibilidad y mantenibilidad del código. Además, incorpora nuevas características de diseño y jugabilidad.

Características Nuevas

    Diseño de Caracteres Personalizado: Los elementos del juego tienen un nuevo aspecto:

        Jugador: <x>

        Enemigos: (<|>)

        Balas: o

    Muros Fronterizos: El área de juego está delimitada por un muro visual:

        Muros horizontales: -

        Muros verticales: |

    Velocidades Decimales: La velocidad de movimiento del jugador, los enemigos y las balas ahora se puede definir con valores decimales, lo que permite un control más fino sobre la dificultad y una sensación de movimiento más fluida (aunque visualmente sigue siendo por caracteres en la terminal).

    Colisiones Ajustadas: La lógica de colisión ha sido adaptada para tener en cuenta el ancho de los nuevos caracteres, asegurando que los disparos y los choques sean precisos.

    Gestión de Entrada Robusta: Se ha implementado un sistema de entrada de teclado directo a la terminal (utilizando sys, tty, termios, select), eliminando dependencias externas problemáticas y mejorando la compatibilidad en entornos Docker.

Estructura del Proyecto

El código está organizado en los siguientes archivos Python para una mejor separación de responsabilidades:

    constants.py: Contiene todas las constantes configurables del juego, como dimensiones de pantalla, caracteres, anchos de elementos, velocidades y puntuación.

    terminal_utils.py: Proporciona funciones de utilidad para interactuar con la terminal, como limpiar la pantalla y configurar/restaurar el modo de entrada raw del teclado.

    player.py: Define la clase Player que representa la nave espacial del jugador, con sus propiedades (posición, carácter, ancho) y métodos de movimiento.

    enemy.py: Define la clase Enemy para los invasores, incluyendo su posición, carácter, ancho y lógica de movimiento.

    bullet.py: Define la clase Bullet para los proyectiles disparados por el jugador, manejando su posición y movimiento.

    game.py: Contiene la clase principal Game, que orquesta toda la lógica del juego: inicialización, renderizado, manejo de entrada, actualización del estado (movimiento de elementos, colisiones, puntuación) y reinicio del juego.

    main.py: El punto de entrada del programa, donde se crea una instancia de Game y se inicia el bucle principal.

Cómo Jugar

    Movimiento: Usa las teclas 'A' y 'D' o las flechas izquierda (←) y derecha (→) para mover tu nave.

    Disparar: Presiona la barra espaciadora para disparar.

    Objetivo: Elimina a todos los invasores antes de que lleguen al muro inferior o colisionen con tu nave.

    Fin del Juego: Si pierdes, presiona 'R' para reiniciar o 'Q' para salir.

Requisitos

Para ejecutar este juego, se necesitara:

    Python 3.x

    No se requieren librerías de Python externas (pip install ...) ya que la gestión de entrada se realiza con módulos nativos.

Ejecución con Docker

La forma recomendada de ejecutar este juego es utilizando Docker, ya que proporciona un entorno aislado y consistente.
1. Estructura del Directorio

Es necesario asegurar que todos los archivos Python (constants.py, terminal_utils.py, player.py, enemy.py, bullet.py, game.py, main.py) y el Dockerfile estén en el mismo directorio (por ejemplo, space_invaders_modular).

space_invaders_modular/
├── Dockerfile
├── main.py
├── game.py
├── player.py
├── enemy.py
├── bullet.py
├── constants.py
└── terminal_utils.py

2. Dockerfile

El Dockerfile es simple y se encarga de crear el entorno necesario:

    # Usar una imagen base de Python ligera
    FROM python:3.9-slim-buster

    # Establece el directorio de trabajo dentro del contenedor
    WORKDIR /app

    # Copia todos los archivos Python del juego al directorio de trabajo
    COPY . /app/

    # No necesitamos instalar librerías adicionales ya que la gestión de entrada es nativa
    # y no hay otras dependencias de pip en esta versión.

    # Comando para ejecutar el juego cuando el contenedor inicie
    CMD ["python", "main.py"]

3. Construir la Imagen Docker

Abrir la terminal, navegar hasta el directorio space_invaders_modular y ejecutar el siguiente comando para construir la imagen Docker:

docker build -t space-invaders-modular .

Esto creará una imagen Docker llamada space-invaders-modular.
4. Ejecutar el Contenedor Docker

Una vez que la imagen esté construida, se puede iniciar el juego ejecutando:

docker run -it space-invaders-modular

El flag -it es crucial para permitir la interacción del teclado con el juego en la terminal.

