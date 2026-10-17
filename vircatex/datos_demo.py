"""Datos de ejemplo para probar el sistema sin tener que digitar todo."""

from datetime import date

from .descuentos import DescuentoPorVolumen
from .empresas import Cliente, Proveedor
from .fabrica import FabricaPrendas


def cargar_datos_demo(sistema):
    sistema.registrar_cliente(Cliente("CL01", "Nordic Basics AB", "Suecia",
                                      "compras@nordicbasics.se", "frecuente", 0.07))
    sistema.registrar_cliente(Cliente("CL02", "Sunset Apparel Inc.", "Estados Unidos",
                                      "sourcing@sunsetapparel.com", "nuevo", 0.08))
    sistema.registrar_cliente(Cliente("CL03", "Maison Laine", "Francia",
                                      "achats@maisonlaine.fr", "nuevo", 0.10))

    sistema.registrar_proveedor(Proveedor("PR01", "Confecciones Gamarra SAC",
                                          "ventas@confgamarra.pe", "20512345678",
                                          "punto", 15000))
    sistema.registrar_proveedor(Proveedor("PR02", "Textil Andina EIRL",
                                          "produccion@textilandina.pe", "20498765432",
                                          "plano", 8000))
    sistema.registrar_proveedor(Proveedor("PR03", "Tejidos Arequipa SAC",
                                          "contacto@tejidosaqp.pe", "20456789123",
                                          "punto", 4000))

    prendas = [
        FabricaPrendas.crear("polo", codigo="P001", descripcion="Pima jersey 40/1",
                             costo_confeccion=1.20, costo_avios=0.30,
                             peso_tela_kg=0.18, precio_kg=11.50),
        FabricaPrendas.crear("polo", codigo="P002", descripcion="Algodón orgánico estampado",
                             costo_confeccion=1.10, costo_avios=0.25,
                             peso_tela_kg=0.20, precio_kg=9.80, estampado=True),
        FabricaPrendas.crear("camisa", codigo="C001", descripcion="Oxford manga larga",
                             costo_confeccion=3.50, costo_avios=0.60,
                             metros_tela=1.60, precio_metro=3.20),
        FabricaPrendas.crear("chompa", codigo="H001", descripcion="Baby alpaca cuello redondo",
                             costo_confeccion=4.00, costo_avios=0.50,
                             peso_hilado_kg=0.35, precio_hilado_kg=38.00, galga=12),
    ]
    for prenda in prendas:
        sistema.registrar_prenda(prenda)

    # dos pedidos de ejemplo
    pedido = sistema.crear_pedido("CL01", "PR01", date(2026, 9, 1))
    pedido.agregar_linea(sistema.buscar_prenda("P001"), 3000)
    pedido.agregar_linea(sistema.buscar_prenda("P002"), 2000)
    pedido.asignar_descuento(DescuentoPorVolumen())
    pedido.cambiar_estado(pedido.EN_PRODUCCION)

    pedido = sistema.crear_pedido("CL02", "PR02", date(2026, 9, 15))
    pedido.agregar_linea(sistema.buscar_prenda("C001"), 1200)
