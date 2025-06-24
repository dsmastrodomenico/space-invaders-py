# bullet.py

import constants

class Bullet:
    """
    Representa un proyectil disparado por el jugador.
    """
    def __init__(self, x, y):
        """
        Inicializa una bala en una posición específica.
        Las posiciones x e y son flotantes.

        Args:
            x (float): Coordenada X inicial de la bala.
            y (float): Coordenada Y inicial de la bala.
        """
        self.x = x
        self.y = y
        self.char = constants.BULLET_CHAR
        self.width = constants.BULLET_WIDTH # Aunque es 1, se mantiene por consistencia

    def move(self):
        """
        Mueve la bala hacia arriba según su velocidad.
        """
        self.y -= constants.BULLET_SPEED

    def get_render_position(self):
        """
        Retorna la posición de la bala como enteros para el renderizado.

        Returns:
            tuple: (x_int, y_int) de la posición de la bala.
        """
        return (int(self.x), int(self.y))

    def is_offscreen(self):
        """
        Comprueba si la bala ha salido de la pantalla (llegó al muro superior).

        Returns:
            bool: True si la bala está fuera de pantalla, False en caso contrario.
        """
        return self.y < 1 # 1 es la fila del muro superior