# constants.py

# Dimensiones de la pantalla de la terminal
SCREEN_WIDTH = 60
SCREEN_HEIGHT = 20

# Caracteres para dibujar los elementos del juego
PLAYER_CHAR = '<x>'
ENEMY_CHAR = '(<|>)'
BULLET_CHAR = 'o'
HORIZONTAL_WALL_CHAR = '-'
VERTICAL_WALL_CHAR = '|'

# Anchos de los caracteres (calculados automáticamente)
PLAYER_WIDTH = len(PLAYER_CHAR)
ENEMY_WIDTH = len(ENEMY_CHAR)
BULLET_WIDTH = len(BULLET_CHAR) # Normalmente 1, pero se define por consistencia

# Velocidades de movimiento
PLAYER_SPEED = 0.8
BULLET_SPEED = 1.1
ENEMY_SPEED = 0.3

# Direcciones
LEFT = -1
RIGHT = 1

# Puntuación
POINTS_PER_ENEMY = 10

# Intervalo de tiempo para el movimiento del enemigo
ENEMY_MOVE_INTERVAL = 0.5 # Segundos