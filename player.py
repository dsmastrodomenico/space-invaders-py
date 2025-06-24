# player.py

import constants

class Player:
    """
    Representa la nave espacial del jugador en el juego.
    """
    def __init__(self, x, y):
        """
        Inicializa la posición del jugador y sus propiedades.
        Las posiciones x e y son flotantes para permitir movimientos decimales.

        Args:
            x (float): Coordenada X inicial del jugador.
            y (float): Coordenada Y inicial del jugador.
        """
        self.x = x
        self.y = y
        self.char = constants.PLAYER_CHAR
        self.width = constants.PLAYER_WIDTH

    def move(self, direction):
        """
        Mueve al jugador horizontalmente dentro de los límites de la pantalla,
        respetando el ancho del personaje y los muros.

        Args:
            direction (int): -1 para izquierda, 1 para derecha.
        """
        self.x += direction * constants.PLAYER_SPEED
        # Asegurarse de que el jugador no se salga de los límites (muros)
        if self.x < 1: # 1 es el borde interior del muro izquierdo
            self.x = 1.0
        if self.x + self.width > constants.SCREEN_WIDTH - 1: # SCREEN_WIDTH - 1 es el borde interior del muro derecho
            self.x = float(constants.SCREEN_WIDTH - 1 - self.width)

    def get_render_position(self):
        """
        Retorna la posición del jugador como enteros para el renderizado.

        Returns:
            tuple: (x_int, y_int) de la posición del jugador.
        """
        return (int(self.x), int(self.y))

    def get_hitbox(self):
        """
        Retorna la caja de colisión del jugador (posición entera y ancho).

        Returns:
            tuple: (x_int, y_int, width)
        """
        return (int(self.x), int(self.y), self.width)