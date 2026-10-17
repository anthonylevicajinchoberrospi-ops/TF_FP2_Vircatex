"""Patrón Singleton: un único objeto que guarda y administra todos los datos.

Sin importar cuántas veces se llame a SistemaVircatex(), siempre se
obtiene la misma instancia, así el menú y los reportes ven la misma información.
"""

from .excepciones import NoEncontradoError, RegistroDuplicadoError
from .pedido import Pedido


class SistemaVircatex:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.reiniciar()
        return cls._instancia

    def reiniciar(self):
        """Borra todos los datos (se usa en las pruebas)."""
        self.clientes = {}
        self.proveedores = {}
        self.prendas = {}
        self.pedidos = {}
        self._siguiente_pedido = 1

    # ---------- métodos genéricos ----------
    @staticmethod
    def _registrar(diccionario, objeto, nombre):
        if objeto.codigo in diccionario:
            raise RegistroDuplicadoError(f"Ya existe un {nombre} con código {objeto.codigo}.")
        diccionario[objeto.codigo] = objeto
        return objeto

    @staticmethod
    def _buscar(diccionario, codigo, nombre):
        objeto = diccionario.get(str(codigo).strip().upper())
        if objeto is None:
            raise NoEncontradoError(f"No existe un {nombre} con código {codigo}.")
        return objeto

    # ---------- clientes ----------
    def registrar_cliente(self, cliente):
        return self._registrar(self.clientes, cliente, "cliente")

    def buscar_cliente(self, codigo):
        return self._buscar(self.clientes, codigo, "cliente")

    def buscar_clientes_por_pais(self, pais):
        return [c for c in self.clientes.values() if c.pais.lower() == pais.strip().lower()]

    # ---------- proveedores ----------
    def registrar_proveedor(self, proveedor):
        for p in self.proveedores.values():
            if p.ruc == proveedor.ruc:
                raise RegistroDuplicadoError(f"El RUC {proveedor.ruc} ya está registrado.")
        return self._registrar(self.proveedores, proveedor, "proveedor")

    def buscar_proveedor(self, codigo):
        return self._buscar(self.proveedores, codigo, "proveedor")

    def proveedores_disponibles(self, especialidad, cantidad):
        """Talleres de esa especialidad con capacidad para la cantidad pedida."""
        return [p for p in self.proveedores.values()
                if p.especialidad == especialidad and p.puede_producir(cantidad)]

    # ---------- prendas ----------
    def registrar_prenda(self, prenda):
        return self._registrar(self.prendas, prenda, "prenda")

    def buscar_prenda(self, codigo):
        return self._buscar(self.prendas, codigo, "prenda")

    # ---------- pedidos ----------
    def crear_pedido(self, codigo_cliente, codigo_proveedor, fecha=None):
        cliente = self.buscar_cliente(codigo_cliente)
        proveedor = self.buscar_proveedor(codigo_proveedor)
        numero = f"PED-{self._siguiente_pedido:04d}"
        pedido = Pedido(numero, cliente, proveedor, fecha)
        self.pedidos[numero] = pedido
        self._siguiente_pedido += 1
        return pedido

    def buscar_pedido(self, numero):
        numero = str(numero).strip().upper()
        if numero.isdigit():  # permite escribir solo "1" en lugar de "PED-0001"
            numero = f"PED-{int(numero):04d}"
        pedido = self.pedidos.get(numero)
        if pedido is None:
            raise NoEncontradoError(f"No existe el pedido {numero}.")
        return pedido

    def pedidos_por_estado(self, estado):
        return [p for p in self.pedidos.values() if p.estado == estado]

    def pedidos_de_cliente(self, codigo_cliente):
        cliente = self.buscar_cliente(codigo_cliente)
        return [p for p in self.pedidos.values() if p.cliente is cliente]

    # ---------- reportes ----------
    def total_comisiones(self):
        """Comisión ganada por Vircatex en pedidos ya embarcados."""
        return round(sum(p.comision() for p in self.pedidos_por_estado(Pedido.EMBARCADO)), 2)

    def tasa_rechazo(self):
        """Porcentaje de pedidos inspeccionados que fueron rechazados."""
        inspeccionados = [p for p in self.pedidos.values() if p.inspeccion is not None]
        if not inspeccionados:
            return 0.0
        rechazados = [p for p in inspeccionados if not p.inspeccion.aprobado()]
        return round(len(rechazados) / len(inspeccionados) * 100, 1)
