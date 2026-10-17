"""Patrón Strategy: distintas formas de calcular el descuento de un pedido.

El Pedido guarda una estrategia y le pide el descuento sin saber cuál es.
"""

from abc import ABC, abstractmethod


class EstrategiaDescuento(ABC):
    @abstractmethod
    def calcular(self, monto, cantidad_prendas):
        """Devuelve el monto a descontar en USD."""

    @abstractmethod
    def nombre(self):
        pass


class SinDescuento(EstrategiaDescuento):
    def calcular(self, monto, cantidad_prendas):
        return 0.0

    def nombre(self):
        return "Sin descuento"


class DescuentoPorVolumen(EstrategiaDescuento):
    """5% desde 3000 prendas y 8% desde 10000 prendas."""

    def calcular(self, monto, cantidad_prendas):
        if cantidad_prendas >= 10000:
            return round(monto * 0.08, 2)
        if cantidad_prendas >= 3000:
            return round(monto * 0.05, 2)
        return 0.0

    def nombre(self):
        return "Descuento por volumen"


class DescuentoClienteFrecuente(EstrategiaDescuento):
    """3% fijo para clientes que ya compraron antes."""

    def calcular(self, monto, cantidad_prendas):
        return round(monto * 0.03, 2)

    def nombre(self):
        return "Descuento cliente frecuente"
