"""Inspección final de calidad por muestreo AQL.

Se usa una tabla simplificada basada en la norma ISO 2859-1
(nivel general II, AQL 2.5), que es la que se usa comúnmente
en la inspección de prendas de exportación.
"""

from .excepciones import DatoInvalidoError

# (tamaño máximo del lote, tamaño de muestra, defectos aceptados)
TABLA_AQL_25 = [
    (50, 5, 0),
    (90, 13, 1),
    (150, 20, 1),
    (280, 32, 2),
    (500, 50, 3),
    (1200, 80, 5),
    (3200, 125, 7),
    (10000, 200, 10),
    (35000, 315, 14),
    (150000, 500, 21),
]


class InspeccionCalidad:
    def __init__(self, tamano_lote):
        if tamano_lote <= 0:
            raise DatoInvalidoError("El lote debe tener al menos una prenda.")
        self.tamano_lote = tamano_lote
        self.muestra, self.aceptacion = self._buscar_en_tabla(tamano_lote)
        self.defectos = None

    @staticmethod
    def _buscar_en_tabla(tamano_lote):
        for maximo, muestra, aceptacion in TABLA_AQL_25:
            if tamano_lote <= maximo:
                # si el lote es más chico que la muestra se revisa todo
                return min(muestra, tamano_lote), aceptacion
        raise DatoInvalidoError("El lote supera las 150000 prendas.")

    def registrar_defectos(self, defectos):
        if defectos < 0 or defectos > self.muestra:
            raise DatoInvalidoError(
                f"Los defectos deben estar entre 0 y {self.muestra} (tamaño de muestra).")
        self.defectos = defectos

    def aprobado(self):
        if self.defectos is None:
            raise DatoInvalidoError("Primero registre los defectos encontrados.")
        return self.defectos <= self.aceptacion

    def resumen(self):
        texto = (f"Lote: {self.tamano_lote} | Muestra: {self.muestra} | "
                 f"Máx. defectos permitidos: {self.aceptacion}")
        if self.defectos is not None:
            resultado = "APROBADO" if self.aprobado() else "RECHAZADO"
            texto += f" | Defectos: {self.defectos} -> {resultado}"
        return texto
