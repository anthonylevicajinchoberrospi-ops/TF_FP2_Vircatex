"""Patrón Factory: crea la prenda correcta según el tipo que se pida.

Así el menú no necesita saber qué clase concreta instanciar.
"""

from .excepciones import DatoInvalidoError
from .prendas import Camisa, Chompa, Polo


class FabricaPrendas:
    _tipos = {
        "polo": Polo,
        "camisa": Camisa,
        "chompa": Chompa,
    }

    @classmethod
    def tipos_disponibles(cls):
        return list(cls._tipos.keys())

    @classmethod
    def crear(cls, tipo, **datos):
        clase = cls._tipos.get(tipo.lower())
        if clase is None:
            raise DatoInvalidoError(f"Tipo de prenda desconocido: {tipo}")
        return clase(**datos)
