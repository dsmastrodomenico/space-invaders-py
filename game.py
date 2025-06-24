# game.py

import time
import sys # Se importa para sys.exit()

# Importar las clases y constantes necesarias
import constants
import terminal_utils
from player import Player
from enemy import Enemy
from bullet import Bullet

class Game:
    """
    Clase principal del juego Space Invaders para terminal.
    Maneja la lógica del juego, el renderizado y la interacción del usuario.
    """
    def __init__(self):
        """
        Inicializa el juego, el jugador, los enemigos, los disparos y la puntuación.
        """
        # Inicializa al jugador en el centro y cerca del borde inferior, ajustado por el ancho del char
        player_start_x = float((constants.SCREEN_WIDTH - constants.PLAYER_WIDTH) // 2)
        player_start_y = float(constants.SCREEN_HEIGHT - 2)
        self.player = Player(player_start_x, player_start_y)
        
        self.enemies = []
        self.bullets = []
        self.score = 0
        self.game_over = False
        self.last_enemy_move_time = time.time() # Para controlar la cadencia de movimiento del enemigo

        self.setup_enemies() # Llama a la función para configurar los enemigos al inicio

    def setup_enemies(self):
        """
        Inicializa una cuadrícula de enemigos.
        Ajustado para el ancho de los enemigos y los límites del muro.
        """
        self.enemies = []
        # Espaciado horizontal para los enemigos, considerando su ancho
        enemy_spacing_x = constants.ENEMY_WIDTH + 2 # Ancho del enemigo + 2 espacios
        # Calcular cuántos enemigos caben en una fila, respetando los muros laterales
        enemies_per_row = (constants.SCREEN_WIDTH - 2 - constants.ENEMY_WIDTH) // enemy_spacing_x

        # Asegurar que haya al menos un enemigo si el espacio lo permite
        if enemies_per_row <= 0:
            enemies_per_row = 1 if (constants.SCREEN_WIDTH - 2 - constants.ENEMY_WIDTH) >= 0 else 0

        for row in range(3): # Tres filas de enemigos
            for col in range(enemies_per_row):
                # La posición inicial ahora debe considerar el muro izquierdo (columna 1)
                start_x = float(col * enemy_spacing_x + 1)
                # Asegurar que el enemigo completo no se salga del muro derecho
                if start_x + constants.ENEMY_WIDTH <= constants.SCREEN_WIDTH -1:
                    self.enemies.append(Enemy(start_x, float(row + 1)))

    def render(self):
        """
        Dibuja el estado actual del juego en la pantalla de la terminal, incluyendo el muro.
        """
        terminal_utils.clear_screen()
        # Crear una "pantalla" vacía con espacios
        screen = [[' ' for _ in range(constants.SCREEN_WIDTH)] for _ in range(constants.SCREEN_HEIGHT)]

        # --- Dibujar el muro ---
        # Muro superior e inferior (horizontales)
        for x in range(constants.SCREEN_WIDTH):
            screen[0][x] = constants.HORIZONTAL_WALL_CHAR
            screen[constants.SCREEN_HEIGHT - 1][x] = constants.HORIZONTAL_WALL_CHAR

        # Muros laterales (verticales)
        for y in range(constants.SCREEN_HEIGHT):
            screen[y][0] = constants.VERTICAL_WALL_CHAR
            screen[y][constants.SCREEN_WIDTH - 1] = constants.VERTICAL_WALL_CHAR

        # Dibujar jugador
        px, py = self.player.get_render_position()
        if 0 < py < constants.SCREEN_HEIGHT - 1: # Asegurarse de que el jugador no se dibuje sobre el muro superior/inferior
            for i, char_part in enumerate(self.player.char):
                if 0 < px + i < constants.SCREEN_WIDTH - 1: # Asegurarse de no dibujar sobre muros laterales
                    screen[py][px + i] = char_part

        # Dibujar balas
        for bullet in self.bullets:
            bx, by = bullet.get_render_position()
            if 0 < by < constants.SCREEN_HEIGHT - 1 and 0 < bx < constants.SCREEN_WIDTH - 1: # Balas también dentro de los muros
                screen[by][bx] = bullet.char

        # Dibujar enemigos
        for enemy in self.enemies:
            ex, ey = enemy.get_render_position()
            if 0 < ey < constants.SCREEN_HEIGHT - 1: # Enemigos también dentro de los muros
                for i, char_part in enumerate(enemy.char):
                    if 0 < ex + i < constants.SCREEN_WIDTH - 1: # Asegurarse de no dibujar sobre muros laterales
                        screen[ey][ex + i] = char_part

        # Imprimir la pantalla
        for row in screen:
            print(''.join(row))

        # Mostrar puntuación
        print(f"Puntuación: {self.score}")

        if self.game_over:
            print("\n¡GAME OVER!")
            print("Presiona 'R' para reiniciar o 'Q' para salir.")

    def handle_input(self):
        """
        Maneja las entradas del teclado del usuario.
        """
        char = terminal_utils.get_input_char()

        if self.game_over:
            if char: # Procesar solo si se leyó un carácter
                if char == 'r' or char == 'R':
                    self.reset_game()
                elif char == 'q' or char == 'Q':
                    sys.exit() # Salir del programa
            return

        # Manejo de entrada durante el juego
        if char:
            if char == 'a' or char == 'A' or char == '\x1b[D': # 'a' o flecha izquierda
                self.player.move(constants.LEFT)
            elif char == 'd' or char == 'D' or char == '\x1b[C': # 'd' o flecha derecha
                self.player.move(constants.RIGHT)
            elif char == ' ': # Barra espaciadora
                if len(self.bullets) < 3: # Limitar el número de balas en pantalla
                    # Bala aparece desde el centro del jugador
                    px, py = self.player.x, self.player.y
                    self.bullets.append(Bullet(px + self.player.width / 2.0, py - 1.0))

    def update(self):
        """
        Actualiza la lógica del juego (movimiento, colisiones, etc.).
        """
        if self.game_over:
            return

        # Mover balas
        # Filter out bullets that are off-screen
        self.bullets = [bullet for bullet in self.bullets if not bullet.is_offscreen()]
        for bullet in self.bullets:
            bullet.move()

        # Mover enemigos
        current_time = time.time()
        if current_time - self.last_enemy_move_time > constants.ENEMY_MOVE_INTERVAL:
            should_drop = False
            for enemy in self.enemies:
                enemy.move()
                # Comprobar si el enemigo actual golpea el muro lateral
                ex, _ = enemy.get_render_position()
                if ex + enemy.width >= constants.SCREEN_WIDTH - 1 or ex <= 0:
                    should_drop = True
                    break # Un enemigo llegó al borde, todos cambian de dirección y bajan

            if should_drop:
                for enemy in self.enemies:
                    enemy.direction *= -1 # Invertir dirección
                    enemy.drop() # Bajar una fila
            
            self.last_enemy_move_time = current_time

        # Colisiones de balas con enemigos
        bullets_to_remove = []
        enemies_to_remove = []
        for bullet in self.bullets:
            bx, by = bullet.get_render_position() # Posición entera para colisión
            for enemy in self.enemies:
                ex, ey, e_width = enemy.get_hitbox() # Caja de colisión del enemigo

                # Colisión: la bala está en la misma fila Y
                # Y la X de la bala está dentro del rango X del enemigo
                if by == ey and bx >= ex and bx < ex + e_width:
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
                    self.score += constants.POINTS_PER_ENEMY
                    break # Una bala solo puede golpear un enemigo a la vez

        # Eliminar balas y enemigos colisionados
        self.bullets = [b for b in self.bullets if b not in bullets_to_remove]
        self.enemies = [e for e in self.enemies if e not in enemies_to_remove]

        # Comprobar si todos los enemigos han sido eliminados
        if not self.enemies:
            print("\n¡Ganaste! ¡Todos los invasores destruidos!")
            self.game_over = True

        # Comprobar si algún enemigo llegó al jugador o al borde inferior (muro)
        px, py, p_width = self.player.get_hitbox() # Caja de colisión del jugador
        for enemy in self.enemies:
            ex, ey, e_width = enemy.get_hitbox() # Caja de colisión del enemigo
            
            # Un enemigo llega al final de la pantalla (muro inferior)
            if ey + 1 >= constants.SCREEN_HEIGHT - 1: # Considera la línea justo encima del muro inferior
                self.game_over = True
                break
            
            # Colisión de enemigo con jugador (superposición de rectángulos)
            # Solapamiento vertical: están en la misma fila Y
            vertical_overlap = (ey == py)
            
            # Solapamiento horizontal: las cajas de colisión se superponen en X
            horizontal_overlap = not (ex + e_width <= px or px + p_width <= ex)

            if vertical_overlap and horizontal_overlap:
                self.game_over = True
                break

    def reset_game(self):
        """
        Reinicia el estado del juego para una nueva partida.
        """
        # Reinicializa al jugador
        player_start_x = float((constants.SCREEN_WIDTH - constants.PLAYER_WIDTH) // 2)
        player_start_y = float(constants.SCREEN_HEIGHT - 2)
        self.player = Player(player_start_x, player_start_y)

        self.enemies = []
        self.bullets = []
        self.score = 0
        self.game_over = False
        self.last_enemy_move_time = time.time()
        self.setup_enemies() # Vuelve a configurar los enemigos

    def run(self):
        """
        Bucle principal del juego.
        Configura la terminal, ejecuta el bucle de juego y restaura la terminal al finalizar.
        """
        try:
            terminal_utils.set_terminal_raw() # Configurar terminal para entrada raw
            print("Presiona las teclas 'A' o 'D' para moverte, ESPACIO para disparar.")
            
            while True:
                self.handle_input()
                self.update()
                self.render()

                time.sleep(0.1) # Pequeña pausa para controlar la velocidad del juego

        except SystemExit:
            # Captura SystemExit lanzado por sys.exit() en handle_input
            print("\n¡Juego terminado!")
        except Exception as e:
            # Otros errores inesperados
            print(f"\nUn error ocurrió: {e}")
        finally:
            terminal_utils.restore_terminal_settings() # Asegurarse de restaurar la terminal