"""Punto de inicio del programa. Ejecutar con:  python main.py"""

from vircatex.menu import Menu


if __name__ == "__main__":
    try:
        Menu().iniciar()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma terminado por el usuario.")
