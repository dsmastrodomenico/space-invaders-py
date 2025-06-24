import os
import time
import sys
import tty
import termios # Para manejar la configuración de la terminal
import select # Para entrada no bloqueante

# --- Constantes del Juego ---
SCREEN_WIDTH = 60
SCREEN_HEIGHT = 20

# Caracteres para los elementos del juego
PLAYER_CHAR = '<x>'
ENEMY_CHAR = '(<|>)'
BULLET_CHAR = 'o'
HORIZONTAL_WALL_CHAR = '-' # Nuevo carácter para el muro horizontal
VERTICAL_WALL_CHAR = '|'  # Nuevo carácter para el muro vertical

# Anchos de los caracteres
PLAYER_WIDTH = len(PLAYER_CHAR)
ENEMY_WIDTH = len(ENEMY_CHAR)
BULLET_WIDTH = len(BULLET_CHAR)

# Velocidades 
PLAYER_SPEED = 0.8 # Ejemplo: movimiento más lento y preciso
BULLET_SPEED = 1.5 # Ejemplo: balas más rápidas
ENEMY_SPEED = 0.3  # Ejemplo: enemigos más lentos aún

LEFT = -1
RIGHT = 1

POINTS_PER_ENEMY = 10

# --- Variables Globales del Juego ---
# Posición inicial del jugador (centrado y ajustado al ancho del carácter)
player_x = float((SCREEN_WIDTH - PLAYER_WIDTH) // 2) # Cambiado a float
player_y = float(SCREEN_HEIGHT - 2) # Cambiado a float

enemies = []
bullets = []

score = 0
game_over = False
last_enemy_move_time = time.time()
enemy_move_interval = 0.5 # Intervalo en segundos para el movimiento del enemigo

# Variables para el manejo de entrada no bloqueante
old_settings = None

# --- Funciones del Juego ---

def clear_screen():
    """
    Limpia la pantalla de la terminal.
    """
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def setup_enemies():
    """
    Inicializa una cuadrícula de enemigos.
    Ajustado para el ancho de los enemigos.
    """
    global enemies
    enemies = []
    # Espaciado horizontal para los enemigos
    enemy_spacing_x = ENEMY_WIDTH + 2 # Ancho del enemigo + 2 espacios
    enemies_per_row = (SCREEN_WIDTH - 2 - ENEMY_WIDTH) // enemy_spacing_x

    if enemies_per_row <= 0:
        enemies_per_row = 1 if (SCREEN_WIDTH - 2 - ENEMY_WIDTH) >= 0 else 0

    for row in range(3):
        # La posición inicial ahora debe considerar el muro izquierdo
        for col in range(enemies_per_row):
            start_x = float(col * enemy_spacing_x + 1) # Posición inicial float
            if start_x + ENEMY_WIDTH <= SCREEN_WIDTH -1:
                enemies.append({'x': start_x, 'y': float(row + 1), 'direction': 1}) # Posiciones y también floats

def render():
    """
    Dibuja el estado actual del juego en la pantalla de la terminal, incluyendo el muro.
    """
    clear_screen()
    screen = [[' ' for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]

    # --- Dibujar el muro ---
    # Muro superior e inferior (horizontales)
    for x in range(SCREEN_WIDTH):
        screen[0][x] = HORIZONTAL_WALL_CHAR # Borde superior
        screen[SCREEN_HEIGHT - 1][x] = HORIZONTAL_WALL_CHAR # Borde inferior

    # Muros laterales (verticales)
    for y in range(SCREEN_HEIGHT):
        screen[y][0] = VERTICAL_WALL_CHAR # Borde izquierdo
        screen[y][SCREEN_WIDTH - 1] = VERTICAL_WALL_CHAR # Borde derecho

    # Dibujar jugador (usando int() para la posición de renderizado)
    player_render_x = int(player_x)
    player_render_y = int(player_y)
    if 0 < player_render_y < SCREEN_HEIGHT - 1:
        for i, char_part in enumerate(PLAYER_CHAR):
            if 0 < player_render_x + i < SCREEN_WIDTH - 1:
                screen[player_render_y][player_render_x + i] = char_part

    # Dibujar balas (usando int() para las posiciones de renderizado)
    for bullet_pos in bullets:
        bx, by = int(bullet_pos[0]), int(bullet_pos[1])
        if 0 < by < SCREEN_HEIGHT - 1 and 0 < bx < SCREEN_WIDTH - 1:
            screen[by][bx] = BULLET_CHAR

    # Dibujar enemigos (usando int() para las posiciones de renderizado)
    for enemy in enemies:
        ex, ey = int(enemy['x']), int(enemy['y'])
        if 0 < ey < SCREEN_HEIGHT - 1:
            for i, char_part in enumerate(ENEMY_CHAR):
                if 0 < ex + i < SCREEN_WIDTH - 1:
                    screen[ey][ex + i] = char_part

    # Imprimir la pantalla
    for row in screen:
        print(''.join(row))

    # Mostrar puntuación
    print(f"Puntuación: {score}")

    if game_over:
        print("\n¡GAME OVER!")
        print("Presiona 'R' para reiniciar o 'Q' para salir.")

def set_terminal_raw():
    """
    Configura la terminal para el modo 'raw' (lectura de un solo carácter sin eco y sin buffer).
    """
    global old_settings
    if sys.stdin.isatty():
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)
    else:
        print("Advertencia: La entrada estándar no es una terminal. La entrada de teclado puede no funcionar.")


def restore_terminal_settings():
    """
    Restaura la configuración original de la terminal.
    """
    if old_settings and sys.stdin.isatty():
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def get_input_char():
    """
    Intenta leer un carácter de la entrada estándar sin bloquear.
    """
    if not sys.stdin.isatty():
        return None
    
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1)
    return None

def handle_input():
    """
    Maneja las entradas del teclado del usuario leyendo caracteres directamente.
    Ajustado para el movimiento del jugador y el punto de origen del disparo,
    respetando los nuevos límites del muro.
    """
    global player_x, bullets, game_over

    if game_over:
        char = get_input_char()
        if char:
            if char == 'r' or char == 'R':
                reset_game()
            elif char == 'q' or char == 'Q':
                sys.exit()
        return

    char = get_input_char()
    if char:
        if char == 'a' or char == 'A' or char == '\x1b[D': # 'a' o flecha izquierda
            player_x -= PLAYER_SPEED
            # Asegurarse de que el jugador no se salga del muro izquierdo
            if player_x < 1: # 1 es la primera columna dentro del muro
                player_x = float(1)
        elif char == 'd' or char == 'D' or char == '\x1b[C': # 'd' o flecha derecha
            player_x += PLAYER_SPEED
            # Asegurarse de que el jugador no se salga del muro derecho
            if player_x + PLAYER_WIDTH >= SCREEN_WIDTH - 1: # SCREEN_WIDTH - 1 es la columna del muro derecho
                player_x = float(SCREEN_WIDTH - 1 - PLAYER_WIDTH)
        elif char == ' ': # Barra espaciadora
            if len(bullets) < 3:
                # Bala aparece desde el centro del jugador
                bullets.append((player_x + PLAYER_WIDTH / 2.0, player_y - 1.0)) # Disparo con flotantes


def update():
    """
    Actualiza la lógica del juego (movimiento, colisiones, etc.).
    Las posiciones se mantienen como flotantes.
    Las colisiones se comprueban usando la parte entera para la cuadrícula.
    """
    global bullets, enemies, score, game_over, last_enemy_move_time

    if game_over:
        return

    # Mover balas
    new_bullets = []
    for bx, by in bullets:
        new_by = by - BULLET_SPEED # Se mantiene como flotante
        if new_by >= 1: # Las balas desaparecen cuando llegan al muro superior (fila 0)
            new_bullets.append((bx, new_by))
    bullets = new_bullets

    # Mover enemigos
    current_time = time.time()
    if current_time - last_enemy_move_time > enemy_move_interval:
        should_drop = False
        for enemy in enemies:
            enemy['x'] += enemy['direction'] * ENEMY_SPEED # Se mantiene como flotante
            
            # Comprobar si el enemigo actual golpea el muro lateral
            # Usamos int() para la comprobación de límites basada en la cuadrícula
            if int(enemy['x'] + ENEMY_WIDTH) >= SCREEN_WIDTH - 1 or int(enemy['x']) <= 0:
                should_drop = True
                break

        if should_drop:
            for enemy in enemies:
                enemy['direction'] *= -1
                enemy['y'] += 1.0 # Bajar una fila (también como flotante)
        
        last_enemy_move_time = current_time

    # Colisiones de balas con enemigos
    bullets_to_remove_indices = set()
    enemies_to_remove_indices = set()

    for i, bullet_pos in enumerate(bullets):
        # Convertimos las posiciones flotantes a enteros para la comprobación de colisiones en cuadrícula
        bx_int, by_int = int(bullet_pos[0]), int(bullet_pos[1])
        for j, enemy in enumerate(enemies):
            ex_int, ey_int = int(enemy['x']), int(enemy['y'])
            
            # Colisión: la bala está en la misma fila Y
            # Y la X de la bala está dentro del rango X del enemigo
            if by_int == ey_int and bx_int >= ex_int and bx_int < ex_int + ENEMY_WIDTH:
                bullets_to_remove_indices.add(i)
                enemies_to_remove_indices.add(j)
                score += POINTS_PER_ENEMY
                break

    bullets = [bullet for i, bullet in enumerate(bullets) if i not in bullets_to_remove_indices]
    enemies = [enemy for i, enemy in enumerate(enemies) if i not in enemies_to_remove_indices]

    if not enemies:
        print("\n¡Ganaste! ¡Todos los invasores destruidos!")
        game_over = True

    # Comprobar si algún enemigo llegó al jugador o al borde inferior (muro)
    for enemy in enemies:
        ex_int, ey_int = int(enemy['x']), int(enemy['y']) # Posiciones enteras para comprobación de colisión
        
        # Un enemigo llega al final de la pantalla (muro inferior)
        if ey_int + 1 >= SCREEN_HEIGHT - 1: # Considera la línea justo encima del muro inferior
            game_over = True
            break
        
        # Colisión de enemigo con jugador (superposición de rectángulos)
        player_hitbox_y_start = int(player_y)
        enemy_hitbox_y_start = ey_int

        vertical_overlap = (enemy_hitbox_y_start == player_hitbox_y_start)
        
        player_hitbox_x_start = int(player_x)
        enemy_hitbox_x_start = ex_int

        horizontal_overlap = not (enemy_hitbox_x_start + ENEMY_WIDTH <= player_hitbox_x_start or player_hitbox_x_start + PLAYER_WIDTH <= enemy_hitbox_x_start)

        if vertical_overlap and horizontal_overlap:
            game_over = True
            break


def reset_game():
    """
    Reinicia el estado del juego para una nueva partida.
    """
    global player_x, player_y, enemies, bullets, score, game_over, last_enemy_move_time
    player_x = float((SCREEN_WIDTH - PLAYER_WIDTH) // 2) # Posición inicial ajustada
    player_y = float(SCREEN_HEIGHT - 2)
    bullets = []
    score = 0
    game_over = False
    setup_enemies()
    last_enemy_move_time = time.time()

def run_game():
    """
    Bucle principal del juego.
    """
    global game_over

    setup_enemies()
    
    try:
        set_terminal_raw()
        print("Presiona las teclas 'A' o 'D' para moverte, ESPACIO para disparar.")
        
        while True:
            handle_input()
            update()
            render()

            time.sleep(0.1)

    except Exception as e:
        restore_terminal_settings()
        print(f"\nUn error ocurrió: {e}")
    finally:
        restore_terminal_settings()

if __name__ == "__main__":
    run_game()