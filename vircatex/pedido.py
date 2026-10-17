"""Pedido de exportación y sus líneas (composición: el pedido contiene sus líneas)."""

from datetime import date, timedelta

from .calidad import InspeccionCalidad
from .descuentos import SinDescuento
from .excepciones import DatoInvalidoError, OperacionNoPermitidaError


class LineaPedido:
    def __init__(self, prenda, cantidad):
        if cantidad <= 0:
            raise DatoInvalidoError("La cantidad debe ser mayor a cero.")
        self.prenda = prenda
        self.cantidad = cantidad

    def subtotal(self):
        return round(self.prenda.costo_unitario() * self.cantidad, 2)

    def __str__(self):
        return (f"{self.prenda.codigo} {self.prenda.tipo()} {self.prenda.descripcion}"
                f" x {self.cantidad} = ${self.subtotal():,.2f}")


class Pedido:
    REGISTRADO = "Registrado"
    EN_PRODUCCION = "En producción"
    APROBADO = "Aprobado"
    RECHAZADO = "Rechazado"
    EMBARCADO = "Embarcado"

    # a qué estados se puede pasar desde cada estado
    TRANSICIONES = {
        REGISTRADO: [EN_PRODUCCION],
        EN_PRODUCCION: [APROBADO, RECHAZADO],
        RECHAZADO: [EN_PRODUCCION],  # se reprocesa y se vuelve a inspeccionar
        APROBADO: [EMBARCADO],
        EMBARCADO: [],
    }

    PORCENTAJE_ADELANTO = 0.30

    def __init__(self, numero, cliente, proveedor, fecha=None):
        self.numero = numero
        self.cliente = cliente
        self.proveedor = proveedor
        self.fecha = fecha or date.today()
        self.lineas = []
        self.estado = self.REGISTRADO
        self.estrategia_descuento = SinDescuento()
        self.inspeccion = None

    # ---------- control ----------
    def agregar_linea(self, prenda, cantidad):
        if self.estado != self.REGISTRADO:
            raise OperacionNoPermitidaError("Solo se agregan prendas a pedidos registrados.")
        if prenda.tejido != self.proveedor.especialidad:
            raise OperacionNoPermitidaError(
                f"El taller {self.proveedor.razon_social} trabaja tejido "
                f"{self.proveedor.especialidad} y la prenda es de tejido {prenda.tejido}.")
        if not self.proveedor.puede_producir(cantidad):
            raise OperacionNoPermitidaError(
                f"El taller solo tiene {self.proveedor.capacidad_disponible()} "
                "unidades disponibles este mes.")
        self.lineas.append(LineaPedido(prenda, cantidad))
        self.proveedor.unidades_asignadas += cantidad

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in self.TRANSICIONES[self.estado]:
            raise OperacionNoPermitidaError(
                f"No se puede pasar de '{self.estado}' a '{nuevo_estado}'.")
        if nuevo_estado == self.EN_PRODUCCION and not self.lineas:
            raise OperacionNoPermitidaError("El pedido no tiene prendas.")
        if nuevo_estado in (self.APROBADO, self.RECHAZADO) and self.inspeccion is None:
            raise OperacionNoPermitidaError("Falta la inspección de calidad.")
        if nuevo_estado == self.EMBARCADO:
            # al embarcar, el taller vuelve a tener libre esa capacidad
            self.proveedor.unidades_asignadas -= self.total_prendas()
        self.estado = nuevo_estado

    def inspeccionar(self, defectos):
        """Registra la inspección AQL y aprueba o rechaza el pedido."""
        if self.estado != self.EN_PRODUCCION:
            raise OperacionNoPermitidaError("Solo se inspeccionan pedidos en producción.")
        inspeccion = InspeccionCalidad(self.total_prendas())
        inspeccion.registrar_defectos(defectos)
        self.inspeccion = inspeccion
        self.cambiar_estado(self.APROBADO if inspeccion.aprobado() else self.RECHAZADO)
        return inspeccion

    def asignar_descuento(self, estrategia):
        self.estrategia_descuento = estrategia

    # ---------- cálculos ----------
    def total_prendas(self):
        return sum(linea.cantidad for linea in self.lineas)

    def costo_produccion(self):
        """Lo que se le paga al taller."""
        return round(sum(linea.subtotal() for linea in self.lineas), 2)

    def comision(self):
        """Lo que gana Vircatex por el servicio de sourcing."""
        return round(self.costo_produccion() * self.cliente.porcentaje_comision, 2)

    def descuento(self):
        monto = self.costo_produccion() + self.comision()
        return self.estrategia_descuento.calcular(monto, self.total_prendas())

    def precio_fob(self):
        """Precio total que paga el cliente con la mercadería puesta en puerto (Callao)."""
        return round(self.costo_produccion() + self.comision() - self.descuento(), 2)

    def precio_fob_unitario(self):
        if self.total_prendas() == 0:
            return 0.0
        return round(self.precio_fob() / self.total_prendas(), 2)

    def cronograma_pago_proveedor(self, cuotas_saldo=2, dias_entre_cuotas=15):
        """Adelanto del 30% el día del pedido y el saldo en cuotas iguales."""
        if cuotas_saldo < 1:
            raise DatoInvalidoError("Debe haber al menos una cuota de saldo.")
        total = self.costo_produccion()
        adelanto = round(total * self.PORCENTAJE_ADELANTO, 2)
        cuota = round((total - adelanto) / cuotas_saldo, 2)

        cronograma = [("Adelanto", self.fecha, adelanto)]
        for i in range(1, cuotas_saldo + 1):
            fecha_cuota = self.fecha + timedelta(days=dias_entre_cuotas * i)
            cronograma.append((f"Cuota {i}", fecha_cuota, cuota))

        # el redondeo puede dejar unos centavos, se ajustan en la última cuota
        diferencia = round(total - sum(c[2] for c in cronograma), 2)
        if diferencia:
            nombre, fecha_ult, monto = cronograma[-1]
            cronograma[-1] = (nombre, fecha_ult, round(monto + diferencia, 2))
        return cronograma

    def __str__(self):
        return (f"Pedido {self.numero} | {self.fecha:%d/%m/%Y} | {self.cliente.razon_social}"
                f" -> {self.proveedor.razon_social} | {self.total_prendas()} prendas | "
                f"FOB ${self.precio_fob():,.2f} | {self.estado}")
