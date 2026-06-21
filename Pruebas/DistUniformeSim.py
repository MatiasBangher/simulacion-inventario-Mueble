import math
from scipy import stats as st
from Pruebas.PruebaMedia import prueba_media_con_z
from Pruebas.PruebaVarianza import prueba_varianza_con_chi2
from Pruebas.PruebaUniformidad import prueba_uniformidad_con_chi2
from Pruebas.PruebasIndependencia import (
    prueba_corrida_arriba_abajo,
    prueba_corrida_arriba_abajo_media
)


class PruebasEstadisticas:
    """
    Clase para agrupar y ejecutar las 5 pruebas estadísticas básicas sobre
    una secuencia de números pseudoaleatorios r ∈ [0,1).
    """

    def __init__(self, secuencia: list[float], alfa: float = 0.05):
        if len(secuencia) < 10:
            raise ValueError("Se necesitan al menos 10 valores para las pruebas.")
        self.r = secuencia
        self.n = len(secuencia)
        self.alfa = alfa
        self.nivel_confianza = 1 - alfa
        self._z_critico = st.norm.ppf(1 - alfa / 2)

    def ejecutar_todas(self, verbose: bool = True) -> dict:
        p_media = prueba_media_con_z(self.r, self.nivel_confianza)
        p_varianza = prueba_varianza_con_chi2(self.r, self.nivel_confianza)
        p_uniformidad = prueba_uniformidad_con_chi2(self.r, self.nivel_confianza)
        p_corrida_ud = prueba_corrida_arriba_abajo(self.r, self.nivel_confianza)
        p_corrida_media = prueba_corrida_arriba_abajo_media(self.r, self.nivel_confianza)

        resultados = {
            "media": p_media,
            "varianza": p_varianza,
            "uniformidad": p_uniformidad,
            "corrida_ud": p_corrida_ud,
            "corrida_media": p_corrida_media
        }

        if verbose:
            self._imprimir_reporte(resultados)

        return resultados

    def _imprimir_reporte(self, resultados: dict):
        SEP = "─" * 70
        print(f"\n{'=' * 70}")
        print(f"  🧪  REPORTE DE PRUEBAS ESTADÍSTICAS — n={self.n}   α={self.alfa}")
        print(f"{'=' * 70}")
        print(f"  1. Prueba de Media:                           {'✅ APRUEBA' if resultados['media'] else '❌ RECHAZA'}")
        print(f"  2. Prueba de Varianza:                        {'✅ APRUEBA' if resultados['varianza'] else '❌ RECHAZA'}")
        print(f"  3. Prueba de Uniformidad (χ²):                 {'✅ APRUEBA' if resultados['uniformidad'] else '❌ RECHAZA'}")
        print(f"  4. Prueba de Independencia (Corrida ↑↓):       {'✅ APRUEBA' if resultados['corrida_ud'] else '❌ RECHAZA'}")
        print(f"  5. Prueba de Independencia (Corrida de Media): {'✅ APRUEBA' if resultados['corrida_media'] else '❌ RECHAZA'}")
        print(f"{SEP}")
        
        total = sum(1 for v in resultados.values() if v)
        aprueba_todo = total == len(resultados)
        print(f"  RESULTADO GLOBAL: {total}/{len(resultados)} pruebas aprobadas")
        if aprueba_todo:
            print("  ✅ La secuencia es estadísticamente uniforme e independiente.")
        else:
            print("  ⚠️ La secuencia NO superó todas las pruebas estadísticas.")
        print(f"{'=' * 70}\n")
