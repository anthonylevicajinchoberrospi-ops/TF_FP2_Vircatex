import unittest

from vircatex.calidad import InspeccionCalidad
from vircatex.datos_demo import cargar_datos_demo
from vircatex.empresas import Cliente, Proveedor
from vircatex.excepciones import (DatoInvalidoError, NoEncontradoError,
                                  RegistroDuplicadoError)
from vircatex.pedido import Pedido
from vircatex.sistema import SistemaVircatex


class TestSistema(unittest.TestCase):

    def setUp(self):
        self.sistema = SistemaVircatex()
        self.sistema.reiniciar()

    def test_singleton_devuelve_la_misma_instancia(self):
        self.assertIs(SistemaVircatex(), SistemaVircatex())

    def test_registrar_y_buscar_cliente(self):
        self.sistema.registrar_cliente(Cliente("cl1", "Nordic", "Suecia", "a@b.se"))
        self.assertEqual(self.sistema.buscar_cliente("CL1").razon_social, "Nordic")

    def test_cliente_duplicado(self):
        self.sistema.registrar_cliente(Cliente("CL1", "Nordic", "Suecia", "a@b.se"))
        with self.assertRaises(RegistroDuplicadoError):
            self.sistema.registrar_cliente(Cliente("CL1", "Otro", "Chile", "c@d.cl"))

    def test_buscar_inexistente(self):
        with self.assertRaises(NoEncontradoError):
            self.sistema.buscar_proveedor("NADA")

    def test_ruc_duplicado(self):
        self.sistema.registrar_proveedor(
            Proveedor("PR1", "A", "a@a.pe", "20512345678", "punto", 100))
        with self.assertRaises(RegistroDuplicadoError):
            self.sistema.registrar_proveedor(
                Proveedor("PR2", "B", "b@b.pe", "20512345678", "plano", 100))

    def test_validaciones_de_empresa(self):
        with self.assertRaises(DatoInvalidoError):
            Cliente("CL1", "X", "Chile", "correo-sin-arroba")
        with self.assertRaises(DatoInvalidoError):
            Proveedor("PR1", "X", "x@x.pe", "123", "punto", 100)

    def test_datos_demo_y_busquedas(self):
        cargar_datos_demo(self.sistema)
        self.assertEqual(len(self.sistema.pedidos), 2)
        self.assertEqual(len(self.sistema.buscar_clientes_por_pais("suecia")), 1)
        self.assertEqual(self.sistema.buscar_pedido("1").numero, "PED-0001")
        disponibles = self.sistema.proveedores_disponibles("punto", 5000)
        self.assertEqual([p.codigo for p in disponibles], ["PR01"])

    def test_reporte_comisiones_y_rechazo(self):
        cargar_datos_demo(self.sistema)
        pedido = self.sistema.buscar_pedido("PED-0001")
        pedido.inspeccionar(defectos=3)  # 5000 prendas: muestra 200, acepta 10
        pedido.cambiar_estado(Pedido.EMBARCADO)
        self.assertEqual(self.sistema.total_comisiones(), pedido.comision())
        self.assertEqual(self.sistema.tasa_rechazo(), 0.0)


class TestInspeccion(unittest.TestCase):

    def test_tabla_aql(self):
        self.assertEqual((InspeccionCalidad(1000).muestra,
                          InspeccionCalidad(1000).aceptacion), (80, 5))
        self.assertEqual(InspeccionCalidad(5000).muestra, 200)

    def test_lote_pequeno_se_revisa_completo(self):
        self.assertEqual(InspeccionCalidad(3).muestra, 3)

    def test_defectos_mayores_a_la_muestra(self):
        inspeccion = InspeccionCalidad(100)  # muestra 20
        with self.assertRaises(DatoInvalidoError):
            inspeccion.registrar_defectos(25)


if __name__ == "__main__":
    unittest.main()
