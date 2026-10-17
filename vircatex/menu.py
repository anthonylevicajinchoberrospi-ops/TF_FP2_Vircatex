"""Menú de consola. Aquí solo se piden datos y se muestran resultados;
las reglas de negocio están en las clases del modelo."""

from .calidad import InspeccionCalidad
from .datos_demo import cargar_datos_demo
from .descuentos import DescuentoClienteFrecuente, DescuentoPorVolumen, SinDescuento
from .empresas import Cliente, Proveedor
from .entradas import leer_decimal, leer_entero, leer_opcion, leer_si_no, leer_texto
from .excepciones import VircatexError
from .fabrica import FabricaPrendas
from .pedido import Pedido
from .sistema import SistemaVircatex

LINEA = "-" * 70


def titulo(texto):
    print("\n" + LINEA)
    print(texto.upper())
    print(LINEA)


def mostrar_lista(elementos, mensaje_vacio="No hay registros."):
    if not elementos:
        print(mensaje_vacio)
    for elemento in elementos:
        print(" ", elemento)


class Menu:
    def __init__(self):
        self.sistema = SistemaVircatex()

    def elegir(self, nombre_menu, opciones):
        """Muestra un submenú, ejecuta la opción elegida y atrapa los errores."""
        while True:
            titulo(nombre_menu)
            for i, (texto, _) in enumerate(opciones, start=1):
                print(f"  {i}. {texto}")
            print("  0. Volver")
            opcion = leer_entero("Opción: ", 0, len(opciones))
            if opcion == 0:
                return
            accion = opciones[opcion - 1][1]
            try:
                accion()
            except VircatexError as error:
                print(f"\n  ERROR: {error}")
            input("\nPresione Enter para continuar...")

    def iniciar(self):
        while True:
            titulo("Vircatex International Sourcing SAC - Gestión de pedidos de exportación")
            print("  1. Clientes")
            print("  2. Proveedores (talleres)")
            print("  3. Prendas y costeo")
            print("  4. Pedidos")
            print("  5. Reportes")
            print("  6. Cargar datos de ejemplo")
            print("  0. Salir")
            opcion = leer_entero("Opción: ", 0, 6)
            if opcion == 0:
                print("Hasta luego.")
                break
            elif opcion == 1:
                self.elegir("Clientes", [
                    ("Registrar cliente", self.registrar_cliente),
                    ("Buscar cliente por código", self.buscar_cliente),
                    ("Buscar clientes por país", self.buscar_clientes_pais),
                    ("Listar clientes", lambda: mostrar_lista(list(self.sistema.clientes.values()))),
                ])
            elif opcion == 2:
                self.elegir("Proveedores", [
                    ("Registrar proveedor", self.registrar_proveedor),
                    ("Buscar proveedor por código",
                     lambda: print(" ", self.sistema.buscar_proveedor(leer_texto("Código: ")))),
                    ("Listar proveedores", lambda: mostrar_lista(list(self.sistema.proveedores.values()))),
                    ("Talleres con capacidad disponible", self.proveedores_disponibles),
                ])
            elif opcion == 3:
                self.elegir("Prendas", [
                    ("Registrar prenda", self.registrar_prenda),
                    ("Buscar prenda por código", self.buscar_prenda),
                    ("Listar prendas", lambda: mostrar_lista(list(self.sistema.prendas.values()))),
                ])
            elif opcion == 4:
                self.elegir("Pedidos", [
                    ("Crear pedido", self.crear_pedido),
                    ("Ver cotización de un pedido", self.ver_pedido),
                    ("Cambiar descuento", self.cambiar_descuento),
                    ("Enviar a producción", lambda: self.cambiar_estado(Pedido.EN_PRODUCCION)),
                    ("Registrar inspección de calidad", self.inspeccionar),
                    ("Embarcar pedido", lambda: self.cambiar_estado(Pedido.EMBARCADO)),
                    ("Cronograma de pago al taller", self.cronograma),
                    ("Listar pedidos", self.listar_pedidos),
                ])
            elif opcion == 5:
                self.reportes()
            elif opcion == 6:
                self.cargar_demo()

    # ---------------- clientes ----------------
    def registrar_cliente(self):
        titulo("Registrar cliente")
        cliente = Cliente(
            codigo=leer_texto("Código: "),
            razon_social=leer_texto("Razón social: "),
            pais=leer_texto("País: "),
            email=leer_texto("Email: "),
            categoria=leer_opcion("Categoría", list(Cliente.CATEGORIAS)),
            porcentaje_comision=leer_decimal("Comisión de Vircatex (%): ") / 100,
        )
        self.sistema.registrar_cliente(cliente)
        print("Cliente registrado:", cliente)

    def buscar_cliente(self):
        cliente = self.sistema.buscar_cliente(leer_texto("Código del cliente: "))
        print(" ", cliente)
        print("  Pedidos:")
        mostrar_lista(self.sistema.pedidos_de_cliente(cliente.codigo), "  (sin pedidos)")

    def buscar_clientes_pais(self):
        pais = leer_texto("País: ")
        mostrar_lista(self.sistema.buscar_clientes_por_pais(pais),
                      f"No hay clientes de {pais}.")

    # ---------------- proveedores ----------------
    def registrar_proveedor(self):
        titulo("Registrar proveedor")
        proveedor = Proveedor(
            codigo=leer_texto("Código: "),
            razon_social=leer_texto("Razón social: "),
            email=leer_texto("Email: "),
            ruc=leer_texto("RUC: "),
            especialidad=leer_opcion("Especialidad", list(Proveedor.ESPECIALIDADES)),
            capacidad_mensual=leer_entero("Capacidad mensual (unidades): ", 1),
        )
        self.sistema.registrar_proveedor(proveedor)
        print("Proveedor registrado:", proveedor)

    def proveedores_disponibles(self):
        especialidad = leer_opcion("Especialidad", list(Proveedor.ESPECIALIDADES))
        cantidad = leer_entero("Cantidad a producir: ", 1)
        mostrar_lista(self.sistema.proveedores_disponibles(especialidad, cantidad),
                      "Ningún taller tiene esa capacidad libre.")

    # ---------------- prendas ----------------
    def registrar_prenda(self):
        titulo("Registrar prenda")
        tipo = leer_opcion("Tipo de prenda", FabricaPrendas.tipos_disponibles())
        datos = {
            "codigo": leer_texto("Código: "),
            "descripcion": leer_texto("Descripción: "),
            "costo_confeccion": leer_decimal("Costo de confección por unidad (USD): "),
            "costo_avios": leer_decimal("Costo de avíos por unidad (USD): "),
        }
        # cada tipo pide los datos de su material
        if tipo == "polo":
            datos["peso_tela_kg"] = leer_decimal("Peso de tela por prenda (kg): ")
            datos["precio_kg"] = leer_decimal("Precio de la tela por kg (USD): ")
            datos["estampado"] = leer_si_no("¿Lleva estampado?")
        elif tipo == "camisa":
            datos["metros_tela"] = leer_decimal("Metros de tela por prenda: ")
            datos["precio_metro"] = leer_decimal("Precio por metro (USD): ")
        else:
            datos["peso_hilado_kg"] = leer_decimal("Peso de hilado por prenda (kg): ")
            datos["precio_hilado_kg"] = leer_decimal("Precio del hilado por kg (USD): ")
            datos["galga"] = leer_entero("Galga (3, 5, 7 o 12): ")

        prenda = FabricaPrendas.crear(tipo, **datos)
        self.sistema.registrar_prenda(prenda)
        print("Prenda registrada:", prenda)

    def buscar_prenda(self):
        prenda = self.sistema.buscar_prenda(leer_texto("Código de la prenda: "))
        print(" ", prenda)
        print(f"  Material: ${prenda.costo_material():.2f} | Confección: "
              f"${prenda.costo_confeccion:.2f} | Avíos: ${prenda.costo_avios:.2f}")

    # ---------------- pedidos ----------------
    def crear_pedido(self):
        titulo("Crear pedido")
        mostrar_lista(list(self.sistema.clientes.values()), "Primero registre un cliente.")
        codigo_cliente = leer_texto("Código del cliente: ")
        self.sistema.buscar_cliente(codigo_cliente)  # valida antes de seguir
        mostrar_lista(list(self.sistema.proveedores.values()), "Primero registre un proveedor.")
        pedido = self.sistema.crear_pedido(codigo_cliente, leer_texto("Código del taller: "))
        print(f"Se creó el pedido {pedido.numero}. Ahora agregue las prendas.")

        mostrar_lista(list(self.sistema.prendas.values()))
        while True:
            try:
                prenda = self.sistema.buscar_prenda(leer_texto("Código de prenda: "))
                cantidad = leer_entero("Cantidad: ", 1)
                pedido.agregar_linea(prenda, cantidad)
                print("  Agregado.")
            except VircatexError as error:
                print(f"  ERROR: {error}")
            if not leer_si_no("¿Agregar otra prenda?"):
                break

        if pedido.cliente.categoria == "frecuente":
            pedido.asignar_descuento(DescuentoClienteFrecuente())
        self.mostrar_cotizacion(pedido)

    def pedir_pedido(self):
        return self.sistema.buscar_pedido(leer_texto("Número de pedido (ej. 1 o PED-0001): "))

    def mostrar_cotizacion(self, pedido):
        titulo(f"Cotización {pedido.numero}")
        print(f"Cliente : {pedido.cliente.razon_social} ({pedido.cliente.pais})")
        print(f"Taller  : {pedido.proveedor.razon_social}")
        print(f"Estado  : {pedido.estado}")
        print("Prendas :")
        mostrar_lista(pedido.lineas, "  (sin prendas)")
        comision = f"Comisión Vircatex ({pedido.cliente.porcentaje_comision:.0%})"
        print()
        print(f"  {'Total de prendas':<30}{pedido.total_prendas():>14,}")
        print(f"  {'Costo de producción (taller)':<30}{pedido.costo_produccion():>14,.2f}")
        print(f"  {comision:<30}{pedido.comision():>14,.2f}")
        print(f"  {pedido.estrategia_descuento.nombre():<30}{-pedido.descuento():>14,.2f}")
        print(f"  {'PRECIO FOB TOTAL (USD)':<30}{pedido.precio_fob():>14,.2f}")
        print(f"  {'Precio FOB por prenda (USD)':<30}{pedido.precio_fob_unitario():>14,.2f}")
        if pedido.inspeccion:
            print("  Inspección:", pedido.inspeccion.resumen())

    def ver_pedido(self):
        self.mostrar_cotizacion(self.pedir_pedido())

    def cambiar_descuento(self):
        pedido = self.pedir_pedido()
        estrategias = {
            "ninguno": SinDescuento(),
            "volumen": DescuentoPorVolumen(),
            "frecuente": DescuentoClienteFrecuente(),
        }
        eleccion = leer_opcion("Tipo de descuento", list(estrategias.keys()))
        pedido.asignar_descuento(estrategias[eleccion])
        print(f"Nuevo precio FOB: ${pedido.precio_fob():,.2f}")

    def cambiar_estado(self, nuevo_estado):
        pedido = self.pedir_pedido()
        pedido.cambiar_estado(nuevo_estado)
        print(f"El pedido {pedido.numero} ahora está: {pedido.estado}")

    def inspeccionar(self):
        pedido = self.pedir_pedido()
        if pedido.estado == Pedido.RECHAZADO:
            # un lote rechazado se reprocesa y vuelve a producción antes de inspeccionarse
            pedido.cambiar_estado(Pedido.EN_PRODUCCION)
        if pedido.estado == Pedido.EN_PRODUCCION:
            # se muestra cuántas prendas revisar antes de pedir los defectos
            print(InspeccionCalidad(pedido.total_prendas()).resumen())
        defectos = leer_entero("Defectos encontrados en la muestra: ", 0)
        inspeccion = pedido.inspeccionar(defectos)
        print(inspeccion.resumen())
        print(f"El pedido quedó: {pedido.estado}")

    def cronograma(self):
        pedido = self.pedir_pedido()
        cuotas = leer_entero("Número de cuotas para el saldo (1-6): ", 1, 6)
        titulo(f"Cronograma de pago al taller - {pedido.numero}")
        print(f"{'Concepto':<12}{'Fecha':<14}{'Monto (USD)':>14}")
        for concepto, fecha, monto in pedido.cronograma_pago_proveedor(cuotas):
            print(f"{concepto:<12}{fecha:%d/%m/%Y}    {monto:>14,.2f}")
        print(f"{'TOTAL':<26}{pedido.costo_produccion():>14,.2f}")

    def listar_pedidos(self):
        if leer_si_no("¿Filtrar por estado?"):
            estados = list(Pedido.TRANSICIONES.keys())
            for i, estado in enumerate(estados, start=1):
                print(f"  {i}. {estado}")
            estado = estados[leer_entero("Estado: ", 1, len(estados)) - 1]
            mostrar_lista(self.sistema.pedidos_por_estado(estado))
        else:
            mostrar_lista(list(self.sistema.pedidos.values()))

    # ---------------- reportes y datos ----------------
    def reportes(self):
        titulo("Reporte general")
        print(f"Clientes: {len(self.sistema.clientes)} | Talleres: "
              f"{len(self.sistema.proveedores)} | Prendas: {len(self.sistema.prendas)}")
        print("Pedidos por estado:")
        for estado in Pedido.TRANSICIONES:
            print(f"  {estado:<15}: {len(self.sistema.pedidos_por_estado(estado))}")
        print(f"Comisiones ganadas (pedidos embarcados): ${self.sistema.total_comisiones():,.2f}")
        print(f"Tasa de rechazo en inspección: {self.sistema.tasa_rechazo()}%")
        input("\nPresione Enter para continuar...")

    def cargar_demo(self):
        try:
            cargar_datos_demo(self.sistema)
            print("Datos de ejemplo cargados.")
        except VircatexError:
            print("Los datos de ejemplo ya estaban cargados.")
