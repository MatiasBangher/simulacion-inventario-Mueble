import unittest
import os
from Pruebas.GenNumsAleatorios import GeneradorCongruencial
from Pruebas.PruebaMedia import prueba_media_con_z
from Pruebas.PruebaVarianza import prueba_varianza_con_chi2
from Pruebas.PruebaUniformidad import prueba_uniformidad_con_chi2
from Pruebas.PruebasIndependencia import (
    prueba_corrida_arriba_abajo,
    prueba_corrida_arriba_abajo_media
)
from Generadores.Demanda import GeneradorDemanda
from Generadores.DiasDemora import GeneradorDemora
from datos import cargar_parametros


class TestSimulacionInventario(unittest.TestCase):

    def setUp(self):
        # Semilla y parámetros típicos para pruebas unitarias
        self.gen = GeneradorCongruencial(X0=12345, a=1103515245, c=12345, m=2**31)

    def test_generador_congruencial(self):
        numeros = self.gen.generar_n(100)
        self.assertEqual(len(numeros), 100)
        self.assertEqual(self.gen.count, 100)
        for r in numeros:
            self.assertTrue(0 <= r < 1)

    def test_pruebas_estadisticas_pasan_con_buenos_datos(self):
        # Generar secuencia grande uniforme para verificar que no lancen errores
        numeros = self.gen.generar_n(500)
        
        # Deben retornar booleanos
        self.assertIsInstance(prueba_media_con_z(numeros, 0.95), bool)
        self.assertIsInstance(prueba_varianza_con_chi2(numeros, 0.95), bool)
        self.assertIsInstance(prueba_uniformidad_con_chi2(numeros, 0.95), bool)
        self.assertIsInstance(prueba_corrida_arriba_abajo(numeros, 0.95), bool)
        self.assertIsInstance(prueba_corrida_arriba_abajo_media(numeros, 0.95), bool)

    def test_generador_demora(self):
        gen_demora = GeneradorDemora(self.gen, de_min=2, de_max=5)
        for _ in range(50):
            val = gen_demora.siguiente()
            self.assertTrue(2 <= val <= 5)

    def test_generador_demanda(self):
        # poisson con lambda = 1.54, a=0, b=4, M=0.35
        gen_demanda = GeneradorDemanda(self.gen, lam=1.54, a=0, b=4, M=0.35)
        for _ in range(50):
            val = gen_demanda.siguiente()
            self.assertTrue(0 <= val <= 4)

    def test_datos_existentes(self):
        # Verificar que los archivos CSV existan y carguen bien
        self.assertTrue(os.path.exists("Tablas - nro_pseudo.csv"))
        self.assertTrue(os.path.exists("Tablas - M. Rechazo.csv"))
        self.assertTrue(os.path.exists("Tablas - Trasnformada Inversa.csv"))
        self.assertTrue(os.path.exists("Tablas - Mueble-Camilo.csv"))
        
        params = cargar_parametros()
        self.assertIn("params_cong", params)
        self.assertIn("params_rechazo", params)
        self.assertIn("params_uniforme", params)
        self.assertIn("df_diario", params)
        self.assertIn("df_pedidos", params)


if __name__ == "__main__":
    unittest.main()
