"""Prendas que Vircatex cotiza y exporta.

Prenda es abstracta: cada tipo de prenda calcula el costo de su material
de forma distinta (polimorfismo). Los montos están en dólares (USD).
"""

from abc import ABC, abstractmethod

from .excepciones import DatoInvalidoError


def _validar_positivo(valor, nombre):
    if valor < 0:
        raise DatoInvalidoError(f"{nombre} no puede ser negativo.")


class Prenda(ABC):
    tejido = ""  # "punto" o "plano", lo define cada subclase

    def __init__(self, codigo, descripcion, costo_confeccion, costo_avios):
        if not codigo.strip() or not descripcion.strip():
            raise DatoInvalidoError("El código y la descripción son obligatorios.")
        _validar_positivo(costo_confeccion, "El costo de confección")
        _validar_positivo(costo_avios, "El costo de avíos")
        self.codigo = codigo.strip().upper()
        self.descripcion = descripcion.strip()
        self.costo_confeccion = costo_confeccion
        self.costo_avios = costo_avios

    @abstractmethod
    def costo_material(self):
        """Costo de la tela o hilado de una unidad."""

    @abstractmethod
    def tipo(self):
        pass

    def costo_unitario(self):
        total = self.costo_material() + self.costo_confeccion + self.costo_avios
        return round(total, 2)

    def __str__(self):
        return (f"{self.codigo} - {self.tipo()} {self.descripcion} "
                f"(tejido {self.tejido}) | costo unit. ${self.costo_unitario():.2f}")


class Polo(Prenda):
    """Polo de tejido de punto. La tela se compra por kilo."""

    tejido = "punto"
    COSTO_ESTAMPADO = 0.35

    def __init__(self, codigo, descripcion, costo_confeccion, costo_avios,
                 peso_tela_kg, precio_kg, estampado=False):
        super().__init__(codigo, descripcion, costo_confeccion, costo_avios)
        _validar_positivo(peso_tela_kg, "El peso de tela")
        _validar_positivo(precio_kg, "El precio por kilo")
        self.peso_tela_kg = peso_tela_kg
        self.precio_kg = precio_kg
        self.estampado = estampado

    def tipo(self):
        return "Polo"

    def costo_material(self):
        return self.peso_tela_kg * self.precio_kg

    def costo_unitario(self):
        # El polo estampado suma el costo del estampado al costo normal
        costo = super().costo_unitario()
        if self.estampado:
            costo += self.COSTO_ESTAMPADO
        return round(costo, 2)


class Camisa(Prenda):
    """Camisa de tejido plano. La tela se compra por metro y se pierde un % en el corte."""

    tejido = "plano"
    MERMA_CORTE = 0.05

    def __init__(self, codigo, descripcion, costo_confeccion, costo_avios,
                 metros_tela, precio_metro):
        super().__init__(codigo, descripcion, costo_confeccion, costo_avios)
        _validar_positivo(metros_tela, "Los metros de tela")
        _validar_positivo(precio_metro, "El precio por metro")
        self.metros_tela = metros_tela
        self.precio_metro = precio_metro

    def tipo(self):
        return "Camisa"

    def costo_material(self):
        return self.metros_tela * (1 + self.MERMA_CORTE) * self.precio_metro


class Chompa(Prenda):
    """Chompa tejida (punto) con hilado de alpaca o algodón. Se paga el hilado y el tejido."""

    tejido = "punto"
    COSTO_TEJIDO_POR_GALGA = 0.40  # a mayor galga, tejido más fino y caro

    def __init__(self, codigo, descripcion, costo_confeccion, costo_avios,
                 peso_hilado_kg, precio_hilado_kg, galga):
        super().__init__(codigo, descripcion, costo_confeccion, costo_avios)
        _validar_positivo(peso_hilado_kg, "El peso del hilado")
        _validar_positivo(precio_hilado_kg, "El precio del hilado")
        if galga not in (3, 5, 7, 12):
            raise DatoInvalidoError("La galga debe ser 3, 5, 7 o 12.")
        self.peso_hilado_kg = peso_hilado_kg
        self.precio_hilado_kg = precio_hilado_kg
        self.galga = galga

    def tipo(self):
        return "Chompa"

    def costo_material(self):
        hilado = self.peso_hilado_kg * self.precio_hilado_kg
        tejido = self.galga * self.COSTO_TEJIDO_POR_GALGA
        return hilado + tejido
