"""Funciones para leer datos por teclado validando lo que escribe el usuario.

Cada función repite la pregunta hasta que el dato sea correcto, así el
programa no se cae si el usuario escribe letras donde va un número.
"""


def leer_texto(mensaje, obligatorio=True):
    while True:
        texto = input(mensaje).strip()
        if texto or not obligatorio:
            return texto
        print("  ! Este dato es obligatorio.")


def leer_entero(mensaje, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(mensaje))
        except ValueError:
            print("  ! Ingrese un número entero.")
            continue
        if minimo is not None and valor < minimo:
            print(f"  ! El valor mínimo es {minimo}.")
        elif maximo is not None and valor > maximo:
            print(f"  ! El valor máximo es {maximo}.")
        else:
            return valor


def leer_decimal(mensaje, minimo=0.0):
    while True:
        try:
            valor = float(input(mensaje).replace(",", "."))
        except ValueError:
            print("  ! Ingrese un número (use punto para los decimales).")
            continue
        if valor < minimo:
            print(f"  ! El valor no puede ser menor a {minimo}.")
        else:
            return valor


def leer_opcion(mensaje, opciones):
    """Pide un valor que debe estar dentro de la lista de opciones."""
    texto_opciones = "/".join(opciones)
    while True:
        valor = input(f"{mensaje} ({texto_opciones}): ").strip().lower()
        if valor in opciones:
            return valor
        print(f"  ! Elija una de estas opciones: {texto_opciones}")


def leer_si_no(mensaje):
    return leer_opcion(mensaje, ["s", "n"]) == "s"
