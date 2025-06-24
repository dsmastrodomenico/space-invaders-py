import os
import time
import sys
import tty
import termios # Para manejar la configuración de la terminal

# --- Constantes del Juego ---
SCREEN_WIDTH = 60
SCREEN_HEIGHT = 20

PLAYER_CHAR = '<x>'
ENEMY_CHAR = '(<|>)'
BULLET_CHAR = 'o'

# Anchos de los caracteres (calculados automáticamente para mayor flexibilidad)
PLAYER_WIDTH = len(PLAYER_CHAR)
ENEMY_WIDTH = len(ENEMY_CHAR)
BULLET_WIDTH = len(BULLET_CHAR) # Normalmente 1, pero se define por consistencia

PLAYER_SPEED = 1
BULLET_SPEED = 1
ENEMY_SPEED = 0.5

LEFT = -1
RIGHT = 1

POINTS_PER_ENEMY = 10

# --- Variables Globales del Juego ---
player_x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
player_y = SCREEN_HEIGHT - 2 # cerca del borde inferior de la altura de la pantalla

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
    enemies_per_row = (SCREEN_WIDTH - ENEMY_WIDTH) // enemy_spacing_x

    for row in range(3):
        for col in range(enemies_per_row):
            # Calcular la posición inicial de cada enemigo
            start_x = col * enemy_spacing_x + 1
            enemies.append({'x': start_x, 'y': row + 1, 'direction': 1})

def render():
    """
    Dibuja el estado actual del juego en la pantalla de la terminal.
    Ajustado para dibujar caracteres de múltiples anchos.
    """
    clear_screen()
    screen = [[' ' for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]

    # Dibujar jugador
    # Iterar sobre el ancho del carácter para colocarlo
    if 0 <= player_y < SCREEN_HEIGHT:
        for i, char_part in enumerate(PLAYER_CHAR):
            if 0 <= player_x + i < SCREEN_WIDTH:
                screen[player_y][player_x + i] = char_part

    # Dibujar balas
    # Las balas son de 1 carácter, no requieren cambios de iteración, solo posición
    for bullet_pos in bullets:
        bx, by = bullet_pos
        if 0 <= bx < SCREEN_WIDTH and 0 <= by < SCREEN_HEIGHT:
            screen[by][bx] = BULLET_CHAR

    # Dibujar enemigos
    for enemy in enemies:
        ex, ey = int(enemy['x']), int(enemy['y'])
        if 0 <= ey < SCREEN_HEIGHT:
            for i, char_part in enumerate(ENEMY_CHAR):
                if 0 <= ex + i < SCREEN_WIDTH:
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
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin) # Permite leer caracteres sin esperar Enter

def restore_terminal_settings():
    """
    Restaura la configuración original de la terminal.
    """
    if old_settings:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def get_input_char():
    """
    Intenta leer un carácter de la entrada estándar sin bloquear.
    """
    import select
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1)
    return None

def handle_input():
    """
    Maneja las entradas del teclado del usuario leyendo caracteres directamente.
    Ajustado para el movimiento del jugador y el punto de origen del disparo.
    """
    global player_x, bullets, game_over

    # Manejo de entrada cuando el juego ha terminado
    if game_over:
        char = get_input_char()
        if char:
            if char == 'r' or char == 'R':
                reset_game()
            elif char == 'q' or char == 'Q':
                sys.exit() # Salir del programa
        return

    # Manejo de entrada durante el juego
    char = get_input_char()
    if char:
        if char == 'a' or char == 'A' or char == '\x1b[D': # 'a' o flecha izquierda
            player_x -= PLAYER_SPEED
            # Asegurarse de que el jugador no se salga del borde izquierdo
            if player_x < 0:
                player_x = 0
        elif char == 'd' or char == 'D' or char == '\x1b[C': # 'd' o flecha derecha
            player_x += PLAYER_SPEED
            # Asegurarse de que el jugador no se salga del borde derecho
            if player_x + PLAYER_WIDTH > SCREEN_WIDTH: # Considera el ancho del jugador
                player_x = SCREEN_WIDTH - PLAYER_WIDTH
        elif char == ' ': # Barra espaciadora
            if len(bullets) < 3: # Limitar el número de balas en pantalla
                # Bala aparece desde el centro del jugador
                bullets.append((player_x + PLAYER_WIDTH // 2, player_y - 1))

def update():
    """
    Actualiza la lógica del juego (movimiento, colisiones, etc.).
    Ajustado para el movimiento de los enemigos y las colisiones con los nuevos anchos.
    """
    global bullets, enemies, score, game_over, last_enemy_move_time

    if game_over:
        return

    # Mover balas
    new_bullets = []
    for bx, by in bullets:
        new_by = by - BULLET_SPEED
        if new_by >= 0: # Mantener balas dentro de la pantalla (solo Y)
            new_bullets.append((bx, new_by))
    bullets = new_bullets

    # Mover enemigos
    current_time = time.time()
    if current_time - last_enemy_move_time > enemy_move_interval:
        should_drop = False
        for enemy in enemies:
            enemy['x'] += enemy['direction'] * ENEMY_SPEED
            
            # Comprobar si el enemigo actual (su borde más a la derecha o izquierda)
            # golpea el límite de la pantalla.
            if int(enemy['x'] + ENEMY_WIDTH) >= SCREEN_WIDTH or int(enemy['x']) <= 0:
                should_drop = True
                break # Una vez que un enemigo golpea, todos cambian de dirección y bajan

        if should_drop:
            for enemy in enemies:
                enemy['direction'] *= -1
                enemy['y'] += 1 # Bajar una fila
        
        last_enemy_move_time = current_time

    # Colisiones de balas con enemigos
    bullets_to_remove_indices = set()
    enemies_to_remove_indices = set()

    for i, bullet_pos in enumerate(bullets):
        bx, by = bullet_pos
        for j, enemy in enumerate(enemies):
            ex, ey = int(enemy['x']), int(enemy['y'])
            
            # Condición de colisión: la bala está en la misma fila Y
            # Y la X de la bala está dentro del rango X del enemigo
            if by == ey and bx >= ex and bx < ex + ENEMY_WIDTH:
                bullets_to_remove_indices.add(i)
                enemies_to_remove_indices.add(j)
                score += POINTS_PER_ENEMY
                break # Una bala solo puede golpear un enemigo a la vez

    bullets = [bullet for i, bullet in enumerate(bullets) if i not in bullets_to_remove_indices]
    enemies = [enemy for i, enemy in enumerate(enemies) if i not in enemies_to_remove_indices]

    if not enemies:
        print("\n¡Ganaste! ¡Todos los invasores destruidos!")
        game_over = True

    # Comprobar si algún enemigo llegó al jugador o al borde inferior
    for enemy in enemies:
        ex, ey = int(enemy['x']), int(enemy['y'])
        
        # Un enemigo llega al final de la pantalla
        if ey + 1 >= SCREEN_HEIGHT: # Asegura que la parte inferior del enemigo no pase la pantalla
            game_over = True
            break
        
        # Colisión de enemigo con jugador (superposición de rectángulos)
        # Check if enemy's x range overlaps with player's x range AND they are on the same or adjacent rows
        player_hitbox_y_start = player_y
        player_hitbox_y_end = player_y # Jugador de 1 línea de alto

        enemy_hitbox_y_start = ey
        enemy_hitbox_y_end = ey # Enemigo de 1 línea de alto

        # Comprobar solapamiento vertical
        vertical_overlap = not (enemy_hitbox_y_end < player_hitbox_y_start or player_hitbox_y_end < enemy_hitbox_y_start)
        
        # Comprobar solapamiento horizontal
        horizontal_overlap = not (ex + ENEMY_WIDTH <= player_x or player_x + PLAYER_WIDTH <= ex)

        if vertical_overlap and horizontal_overlap:
            game_over = True
            break

def reset_game():
    """
    Reinicia el estado del juego para una nueva partida.
    """
    global player_x, player_y, enemies, bullets, score, game_over, last_enemy_move_time
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_WIDTH - 2
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
    
    # Intenta configurar la terminal para la entrada raw
    try:
        set_terminal_raw()
        # El mensaje de "Presiona cualquier tecla..." ahora debe ser manejado por el juego
        # porque la entrada está en modo raw.
        # No se necesita read_event de keyboard.
        print("Presiona las teclas 'A' o 'D' para moverte, ESPACIO para disparar.")
        
        while True:
            handle_input()
            update()
            render()

            if game_over:
                # El handle_input ya maneja 'r' y 'q' para game_over
                pass
            
            time.sleep(0.1)

    except Exception as e:
        print(f"\nUn error ocurrió: {e}")
    finally:
        restore_terminal_settings() # Asegurarse de restaurar la terminal al salir

if __name__ == "__main__":
    run_game()