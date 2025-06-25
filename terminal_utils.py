# terminal_utils.py

import os
import sys
import tty
import termios
import select

# Variable global para guardar la configuración original de la terminal
_old_terminal_settings = None

def clear_screen():
    """
    Limpia la pantalla de la terminal.
    """
    if os.name == 'nt': # Para sistemas Windows
        _ = os.system('cls')
    else: # Para sistemas Unix/Linux/macOS
        _ = os.system('clear')

def set_terminal_raw():
    """
    Configura la terminal para el modo 'raw' (lectura de un solo carácter sin eco y sin buffer).
    Esto permite la captura instantánea de las pulsaciones de teclas.
    """
    global _old_terminal_settings
    # Asegurarse de que sys.stdin es un tty (terminal interactiva) antes de intentar configurarlo
    if sys.stdin.isatty():
        _old_terminal_settings = termios.tcgetattr(sys.stdin) # Guarda la configuración actual
        tty.setcbreak(sys.stdin) # Configura para lectura de un solo carácter sin eco
    else:
        # Esto puede ocurrir si el script no se ejecuta en una terminal interactiva (ej. con redirección de entrada)
        print("Advertencia: La entrada estándar no es una terminal. La entrada de teclado puede no funcionar como se espera.")

def restore_terminal_settings():
    """
    Restaura la configuración original de la terminal.
    Debe llamarse al finalizar el juego para asegurar que la terminal funcione normalmente.
    """
    if _old_terminal_settings and sys.stdin.isatty(): # Solo restaura si se configuró y es un tty
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, _old_terminal_settings)

def get_input_char():
    """
    Intenta leer un carácter de la entrada estándar sin bloquear.
    Devuelve el carácter leído o None si no hay nada disponible.
    """
    # Si stdin no es una terminal, no intentamos leer input interactivo
    if not sys.stdin.isatty():
        return None
    
    # Comprueba si hay datos disponibles para leer en sys.stdin en 0 segundos (no bloqueante)
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1) # Lee un solo carácter
    return None