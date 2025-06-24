import os
import time
import keyboard # Para detectar las pulsaciones de teclas sin bloquear

# --- Constantes del Juego ---
SCREEN_WIDTH = 60
SCREEN_HEIGHT = 20

PLAYER_CHAR = 'A'
ENEMY_CHAR = 'V'
BULLET_CHAR = '|'
EXPLOSION_CHAR = 'X' 

PLAYER_SPEED = 1
BULLET_SPEED = 1
ENEMY_SPEED = 0.5

LEFT = -1
RIGHT = 1

POINTS_PER_ENEMY = 10

# --- Variables Globales del Juego ---
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_WIDTH - 2 # Cerca del borde inferior

enemies = [] # Lista de tuplas (x, y, direction)
bullets = [] # Lista de tuplas (x, y)

score = 0
game_over = False
last_enemy_move_time = time.time()
enemy_move_interval = 0.5 # Intervalo en segundos para el movimiento del enemigo

# --- Funciones del Juego ---

def clear_screen():
    """
    Limpia la pantalla de la terminal.
    """
    # Para Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Para Unix/Linux/macOS
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
            enemies.append({'x': col * 5 + 2, 'y': row + 1, 'direction': 1}) # dict para facilitar acceso

def render():
    """
    Dibuja el estado actual del juego en la pantalla de la terminal.
    """
    clear_screen()
    # Crear una "pantalla" vacía con espacios
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

def handle_input():
    """
    Maneja las entradas del teclado del usuario.
    """
    global player_x, bullets

    if keyboard.is_pressed('left'):
        player_x -= PLAYER_SPEED
        if player_x < 0:
            player_x = 0
    if keyboard.is_pressed('right'):
        player_x += PLAYER_SPEED
        if player_x >= SCREEN_WIDTH:
            player_x = SCREEN_WIDTH - 1
    if keyboard.is_pressed('space'):
        # Disparar una bala (solo si no hay muchas balas en pantalla para evitar spam)
        if len(bullets) < 3:
            bullets.append((player_x, player_y - 1)) # Bala aparece justo encima del jugador

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
        if new_by >= 0: # Mantener balas dentro de la pantalla
            new_bullets.append((bx, new_by))
    bullets = new_bullets

    # Mover enemigos
    current_time = time.time()
    if current_time - last_enemy_move_time > enemy_move_interval:
        should_drop = False
        for enemy in enemies:
            enemy['x'] += enemy['direction'] * ENEMY_SPEED
            ex = int(enemy['x'])
            # Si un enemigo llega al borde, todos cambian de dirección y bajan
            if ex >= SCREEN_WIDTH - 1 or ex <= 0:
                should_drop = True
                break # Salir del bucle interno para evitar múltiples cambios de dirección
        
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
            if bx == ex and by == ey:
                bullets_to_remove_indices.add(i)
                enemies_to_remove_indices.add(j)
                score += POINTS_PER_ENEMY
                break # Una bala solo puede golpear un enemigo a la vez

    # Eliminar balas y enemigos colisionados
    bullets = [bullet for i, bullet in enumerate(bullets) if i not in bullets_to_remove_indices]
    enemies = [enemy for i, enemy in enumerate(enemies) if i not in enemies_to_remove_indices] # CORREGIDO AQUÍ

    # Comprobar si todos los enemigos han sido eliminados
    if not enemies:
        print("\n¡Ganaste! ¡Todos los invasores destruidos!")
        game_over = True

    # Comprobar si algún enemigo llegó al jugador o al borde inferior
    for enemy in enemies:
        ex, ey = int(enemy['x']), int(enemy['y'])
        if ey >= SCREEN_HEIGHT - 1: # Si el enemigo llega al penúltimo borde
            game_over = True
            break
        # Colisión de enemigo con jugador (simplificado)
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

    setup_enemies() # Configura los enemigos al inicio del juego
    
    print("Presiona cualquier tecla para iniciar el juego...")
    keyboard.read_event(suppress=True) # Espera una pulsación y la suprime

    while True:
        handle_input()
        update()
        render()

        if game_over:
            if keyboard.is_pressed('r'):
                reset_game()
            elif keyboard.is_pressed('q'):
                break
        
        time.sleep(0.1) # Pequeña pausa para controlar la velocidad del juego

if __name__ == "__main__":
    run_game()