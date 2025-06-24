import os
import time
import sys
import tty
import termios # Para manejar la configuración de la terminal

# --- Constantes del Juego ---
SCREEN_WIDTH = 60
SCREEN_HEIGHT = 20

PLAYER_CHAR = 'A'
ENEMY_CHAR = 'V'
BULLET_CHAR = '|'

PLAYER_SPEED = 1
BULLET_SPEED = 1
ENEMY_SPEED = 0.5

LEFT = -1
RIGHT = 1

POINTS_PER_ENEMY = 10

# --- Variables Globales del Juego ---
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_WIDTH - 2

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
    """
    global enemies
    enemies = []
    for row in range(3):
        for col in range(SCREEN_WIDTH // 5):
            enemies.append({'x': col * 5 + 2, 'y': row + 1, 'direction': 1})

def render():
    """
    Dibuja el estado actual del juego en la pantalla de la terminal.
    """
    clear_screen()
    screen = [[' ' for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]

    # Dibujar jugador
    if 0 <= player_x < SCREEN_WIDTH and 0 <= player_y < SCREEN_HEIGHT:
        screen[player_y][player_x] = PLAYER_CHAR

    # Dibujar balas
    for bullet_pos in bullets:
        bx, by = bullet_pos
        if 0 <= bx < SCREEN_WIDTH and 0 <= by < SCREEN_HEIGHT:
            screen[by][bx] = BULLET_CHAR

    # Dibujar enemigos
    for enemy in enemies:
        ex, ey = int(enemy['x']), int(enemy['y'])
        if 0 <= ex < SCREEN_WIDTH and 0 <= ey < SCREEN_HEIGHT:
            screen[ey][ex] = ENEMY_CHAR

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
    """
    global player_x, bullets, game_over

    if game_over:
        char = get_input_char()
        if char == 'r' or char == 'R':
            reset_game()
        elif char == 'q' or char == 'Q':
            sys.exit() # Salir del programa
        return

    char = get_input_char()
    if char == 'a' or char == 'A' or char == '\x1b[D': # 'a' o flecha izquierda
        player_x -= PLAYER_SPEED
        if player_x < 0:
            player_x = 0
    elif char == 'd' or char == 'D' or char == '\x1b[C': # 'd' o flecha derecha
        player_x += PLAYER_SPEED
        if player_x >= SCREEN_WIDTH:
            player_x = SCREEN_WIDTH - 1
    elif char == ' ': # Barra espaciadora
        if len(bullets) < 3:
            bullets.append((player_x, player_y - 1))

def update():
    """
    Actualiza la lógica del juego (movimiento, colisiones, etc.).
    """
    global bullets, enemies, score, game_over, last_enemy_move_time

    if game_over:
        return

    # Mover balas
    new_bullets = []
    for bx, by in bullets:
        new_by = by - BULLET_SPEED
        if new_by >= 0:
            new_bullets.append((bx, new_by))
    bullets = new_bullets

    # Mover enemigos
    current_time = time.time()
    if current_time - last_enemy_move_time > enemy_move_interval:
        should_drop = False
        for enemy in enemies:
            enemy['x'] += enemy['direction'] * ENEMY_SPEED
            ex = int(enemy['x'])
            if ex >= SCREEN_WIDTH - 1 or ex <= 0:
                should_drop = True
                break
        
        if should_drop:
            for enemy in enemies:
                enemy['direction'] *= -1
                enemy['y'] += 1
        
        last_enemy_move_time = current_time

    # Colisiones de balas con enemigos
    bullets_to_remove_indices = set()
    enemies_to_remove_indices = set()

    for i, bullet_pos in enumerate(bullets):
        bx, by = bullet_pos
        for j, enemy in enumerate(enemies):
            ex, ey = int(enemy['x']), int(enemy['y'])
            if bx == ex and by == ey:
                bullets_to_remove_indices.add(i)
                enemies_to_remove_indices.add(j)
                score += POINTS_PER_ENEMY
                break

    bullets = [bullet for i, bullet in enumerate(bullets) if i not in bullets_to_remove_indices]
    enemies = [enemy for i, enemy in enumerate(enemies) if i not in enemies_to_remove_indices]

    if not enemies:
        print("\n¡Ganaste! ¡Todos los invasores destruidos!")
        game_over = True

    for enemy in enemies:
        ex, ey = int(enemy['x']), int(enemy['y'])
        if ey >= SCREEN_HEIGHT - 1:
            game_over = True
            break
        if (ex == player_x and ey == player_y):
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