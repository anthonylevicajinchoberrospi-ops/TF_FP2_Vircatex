"""Excepciones propias del sistema.

Todas heredan de VircatexError para poder atraparlas juntas en el menú.
"""


class VircatexError(Exception):
    """Error general del sistema."""


class DatoInvalidoError(VircatexError):
    """Un dato no cumple las reglas (vacío, negativo, formato incorrecto...)."""


class RegistroDuplicadoError(VircatexError):
    """Se intenta registrar un código que ya existe."""


class NoEncontradoError(VircatexError):
    """La búsqueda no encontró el registro."""


class OperacionNoPermitidaError(VircatexError):
    """La operación no se puede hacer en el estado actual (ej. capacidad del taller)."""
