import unittest

from vircatex.excepciones import DatoInvalidoError
from vircatex.fabrica import FabricaPrendas
from vircatex.prendas import Camisa, Chompa, Polo


class TestPrendas(unittest.TestCase):

    def test_costo_polo(self):
        polo = Polo("P1", "Pima", 1.20, 0.30, peso_tela_kg=0.18, precio_kg=11.50)
        # 0.18 * 11.50 = 2.07  +  1.20  +  0.30
        self.assertEqual(polo.costo_unitario(), 3.57)

    def test_polo_estampado_cuesta_mas(self):
        liso = Polo("P1", "Liso", 1.0, 0.2, 0.2, 10)
        estampado = Polo("P2", "Estampado", 1.0, 0.2, 0.2, 10, estampado=True)
        self.assertAlmostEqual(estampado.costo_unitario() - liso.costo_unitario(), 0.35)

    def test_costo_camisa_incluye_merma(self):
        camisa = Camisa("C1", "Oxford", 3.50, 0.60, metros_tela=1.60, precio_metro=3.20)
        # 1.60 * 1.05 * 3.20 = 5.376  +  3.50  +  0.60 = 9.476
        self.assertEqual(camisa.costo_unitario(), 9.48)

    def test_costo_chompa(self):
        chompa = Chompa("H1", "Alpaca", 4.0, 0.5, peso_hilado_kg=0.35,
                        precio_hilado_kg=38.0, galga=12)
        # hilado 13.30 + tejido 4.80 + 4.00 + 0.50
        self.assertEqual(chompa.costo_unitario(), 22.60)

    def test_polimorfismo_misma_llamada_distinto_calculo(self):
        prendas = [
            Polo("A", "x", 1, 0, 0.2, 10),
            Camisa("B", "x", 1, 0, 1, 10),
            Chompa("C", "x", 1, 0, 0.1, 10, 3),
        ]
        costos = [p.costo_material() for p in prendas]
        self.assertEqual([round(c, 2) for c in costos], [2.0, 10.5, 2.2])

    def test_valor_negativo_lanza_error(self):
        with self.assertRaises(DatoInvalidoError):
            Polo("P1", "x", -1, 0.3, 0.18, 11.5)

    def test_galga_invalida(self):
        with self.assertRaises(DatoInvalidoError):
            Chompa("H1", "x", 4, 0.5, 0.3, 38, galga=9)

    def test_fabrica_crea_la_clase_correcta(self):
        prenda = FabricaPrendas.crear("camisa", codigo="c9", descripcion="Lino",
                                      costo_confeccion=3, costo_avios=0.5,
                                      metros_tela=1.5, precio_metro=4)
        self.assertIsInstance(prenda, Camisa)
        self.assertEqual(prenda.codigo, "C9")

    def test_fabrica_tipo_desconocido(self):
        with self.assertRaises(DatoInvalidoError):
            FabricaPrendas.crear("pantalon", codigo="X")


if __name__ == "__main__":
    unittest.main()
