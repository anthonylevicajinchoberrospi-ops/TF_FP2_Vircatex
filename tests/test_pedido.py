import unittest
from datetime import date

from vircatex.descuentos import (DescuentoClienteFrecuente, DescuentoPorVolumen,
                                 SinDescuento)
from vircatex.empresas import Cliente, Proveedor
from vircatex.excepciones import DatoInvalidoError, OperacionNoPermitidaError
from vircatex.pedido import Pedido
from vircatex.prendas import Camisa, Polo


class TestPedido(unittest.TestCase):

    def setUp(self):
        self.cliente = Cliente("CL1", "Nordic", "Suecia", "a@nordic.se", "nuevo", 0.10)
        self.taller = Proveedor("PR1", "Gamarra SAC", "v@gamarra.pe", "20512345678",
                                "punto", 5000)
        # polo de costo exacto 4.00 para que las cuentas sean fáciles
        self.polo = Polo("P1", "Básico", 1.50, 0.50, peso_tela_kg=0.2, precio_kg=10)
        self.pedido = Pedido("PED-0001", self.cliente, self.taller, date(2026, 9, 1))

    def test_costo_comision_y_fob(self):
        self.pedido.agregar_linea(self.polo, 1000)
        self.assertEqual(self.pedido.costo_produccion(), 4000.00)
        self.assertEqual(self.pedido.comision(), 400.00)
        self.assertEqual(self.pedido.precio_fob(), 4400.00)
        self.assertEqual(self.pedido.precio_fob_unitario(), 4.40)

    def test_descuento_por_volumen(self):
        self.pedido.agregar_linea(self.polo, 3000)
        self.pedido.asignar_descuento(DescuentoPorVolumen())
        # (12000 + 1200) * 5% = 660
        self.assertEqual(self.pedido.descuento(), 660.00)
        self.assertEqual(self.pedido.precio_fob(), 12540.00)

    def test_estrategias_de_descuento(self):
        self.assertEqual(SinDescuento().calcular(1000, 50000), 0)
        self.assertEqual(DescuentoPorVolumen().calcular(1000, 2999), 0)
        self.assertEqual(DescuentoPorVolumen().calcular(1000, 10000), 80)
        self.assertEqual(DescuentoClienteFrecuente().calcular(1000, 1), 30)

    def test_capacidad_del_taller(self):
        self.pedido.agregar_linea(self.polo, 4000)
        self.assertEqual(self.taller.capacidad_disponible(), 1000)
        with self.assertRaises(OperacionNoPermitidaError):
            self.pedido.agregar_linea(self.polo, 1500)

    def test_tejido_debe_coincidir_con_taller(self):
        camisa = Camisa("C1", "Oxford", 3, 0.5, 1.5, 3)
        with self.assertRaises(OperacionNoPermitidaError):
            self.pedido.agregar_linea(camisa, 100)

    def test_cantidad_cero(self):
        with self.assertRaises(DatoInvalidoError):
            self.pedido.agregar_linea(self.polo, 0)

    def test_cronograma_suma_el_total(self):
        self.pedido.agregar_linea(self.polo, 1000)  # 4000 USD
        cronograma = self.pedido.cronograma_pago_proveedor(cuotas_saldo=3)
        self.assertEqual(len(cronograma), 4)
        self.assertEqual(cronograma[0][2], 1200.00)  # adelanto 30%
        self.assertEqual(cronograma[1][1], date(2026, 9, 16))
        self.assertAlmostEqual(sum(c[2] for c in cronograma), 4000.00)

    def test_flujo_de_estados(self):
        self.pedido.agregar_linea(self.polo, 1000)
        self.pedido.cambiar_estado(Pedido.EN_PRODUCCION)
        self.pedido.inspeccionar(defectos=2)  # muestra 80, acepta hasta 5
        self.assertEqual(self.pedido.estado, Pedido.APROBADO)
        self.pedido.cambiar_estado(Pedido.EMBARCADO)
        self.assertEqual(self.taller.unidades_asignadas, 0)  # capacidad liberada

    def test_inspeccion_rechazada(self):
        self.pedido.agregar_linea(self.polo, 1000)
        self.pedido.cambiar_estado(Pedido.EN_PRODUCCION)
        self.pedido.inspeccionar(defectos=6)
        self.assertEqual(self.pedido.estado, Pedido.RECHAZADO)

    def test_no_se_puede_saltar_estados(self):
        self.pedido.agregar_linea(self.polo, 10)
        with self.assertRaises(OperacionNoPermitidaError):
            self.pedido.cambiar_estado(Pedido.EMBARCADO)

    def test_no_produce_pedido_vacio(self):
        with self.assertRaises(OperacionNoPermitidaError):
            self.pedido.cambiar_estado(Pedido.EN_PRODUCCION)


if __name__ == "__main__":
    unittest.main()
