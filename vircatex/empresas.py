"""Clientes y proveedores. Ambos son empresas, por eso heredan de Empresa."""

import re

from .excepciones import DatoInvalidoError


class Empresa:
    """Clase base con los datos comunes de cualquier empresa."""

    def __init__(self, codigo, razon_social, pais, email):
        if not codigo.strip():
            raise DatoInvalidoError("El código no puede estar vacío.")
        if not razon_social.strip():
            raise DatoInvalidoError("La razón social no puede estar vacía.")
        if not re.match(r"^[\w.+-]+@[\w-]+\.[\w.-]+$", email):
            raise DatoInvalidoError(f"Email no válido: {email}")
        self.codigo = codigo.strip().upper()
        self.razon_social = razon_social.strip()
        self.pais = pais.strip()
        self.email = email.strip()

    def tipo(self):
        return "Empresa"

    def ficha(self):
        return f"[{self.tipo()}] {self.codigo} - {self.razon_social} ({self.pais})"

    def __str__(self):
        return self.ficha()


class Cliente(Empresa):
    """Comprador extranjero (marca o tienda) que hace pedidos a Vircatex."""

    CATEGORIAS = ("nuevo", "frecuente")

    def __init__(self, codigo, razon_social, pais, email, categoria="nuevo",
                 porcentaje_comision=0.08):
        super().__init__(codigo, razon_social, pais, email)
        if categoria not in self.CATEGORIAS:
            raise DatoInvalidoError("La categoría debe ser 'nuevo' o 'frecuente'.")
        if not 0 <= porcentaje_comision <= 0.30:
            raise DatoInvalidoError("La comisión debe estar entre 0% y 30%.")
        self.categoria = categoria
        self.porcentaje_comision = porcentaje_comision

    def tipo(self):
        return "Cliente"

    def ficha(self):
        return (super().ficha() + f" | {self.categoria} | "
                f"comisión {self.porcentaje_comision:.0%}")


class Proveedor(Empresa):
    """Taller o fábrica peruana que confecciona las prendas."""

    ESPECIALIDADES = ("punto", "plano")

    def __init__(self, codigo, razon_social, email, ruc, especialidad,
                 capacidad_mensual):
        super().__init__(codigo, razon_social, "Perú", email)
        if not (len(ruc) == 11 and ruc.isdigit() and ruc[:2] in ("10", "20")):
            raise DatoInvalidoError("El RUC debe tener 11 dígitos y empezar en 10 o 20.")
        if especialidad not in self.ESPECIALIDADES:
            raise DatoInvalidoError("La especialidad debe ser 'punto' o 'plano'.")
        if capacidad_mensual <= 0:
            raise DatoInvalidoError("La capacidad mensual debe ser mayor a cero.")
        self.ruc = ruc
        self.especialidad = especialidad
        self.capacidad_mensual = capacidad_mensual
        self.unidades_asignadas = 0

    def tipo(self):
        return "Proveedor"

    def capacidad_disponible(self):
        return self.capacidad_mensual - self.unidades_asignadas

    def puede_producir(self, cantidad):
        return cantidad <= self.capacidad_disponible()

    def ficha(self):
        return (super().ficha() + f" | RUC {self.ruc} | tejido {self.especialidad} | "
                f"disponible {self.capacidad_disponible()}/{self.capacidad_mensual} und")
