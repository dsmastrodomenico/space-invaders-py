# enemy.py

import constants

class Enemy:
    """
    Representa un enemigo (invasor) en el juego.
    """
    def __init__(self, x, y):
        """
        Inicializa un enemigo en una posición específica.
        Las posiciones x e y son flotantes.

        Args:
            x (float): Coordenada X inicial del enemigo.
            y (float): Coordenada Y inicial del enemigo.
        """
        self.x = x
        self.y = y
        self.char = constants.ENEMY_CHAR
        self.width = constants.ENEMY_WIDTH
        self.direction = 1 # 1 para derecha, -1 para izquierda

    def move(self):
        """
        Mueve al enemigo horizontalmente según su velocidad y dirección.
        """
        self.x += self.direction * constants.ENEMY_SPEED

    def drop(self):
        """
        Mueve al enemigo una fila hacia abajo.
        """
        self.y += 1.0 # La posición Y también es flotante

    def get_render_position(self):
        """
        Retorna la posición del enemigo como enteros para el renderizado.

        Returns:
            tuple: (x_int, y_int) de la posición del enemigo.
        """
        return (int(self.x), int(self.y))

    def get_hitbox(self):
        """
        Retorna la caja de colisión del enemigo (posición entera y ancho).

        Returns:
            tuple: (x_int, y_int, width)
        """
        return (int(self.x), int(self.y), self.width)