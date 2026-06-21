from datos import cargar_parametros, imprimir_parametros
from simulacion_actual import simular_actual
from Pruebas.DistUniformeSim import PruebasEstadisticas

# ==============================================================================
# ⚙️ PARÁMETROS CONFIGURABLES  ← Modificar valores aquí
# ==============================================================================

# Costos (en $)
CEP     = 0.0      # Costo de emisión por pedido ($/pedido)
CVP     = 0.0      # Costo de venta perdida ($/unidad)
CALM    = 0.0      # Costo de almacenamiento regular ($/unidad·día)
CSOB    = 0.0      # Costo de almacenamiento sobrante ($/unidad·día)

# Parámetros de Simulación
TF      = 70       # Tiempo final de simulación (días hábiles)
SMR     = 10       # Stock Medio de Referencia (punto de reorden)
MAX_CAP = 10       # Capacidad máxima del depósito
ST_0    = 7        # Stock inicial

# Nivel de significancia para las pruebas estadísticas
ALFA    = 0.05

# Rutas de archivos CSV
CSV_PSEUDO    = "Tablas - nro_pseudo.csv"
CSV_RECHAZO   = "Tablas - M. Rechazo.csv"
CSV_INVERSA   = "Tablas - Trasnformada Inversa.csv"
CSV_HISTORICO = "Tablas - Mueble-Camilo.csv"


if __name__ == "__main__":
    # 1. Cargar parámetros desde los CSVs
    print("Cargando parámetros desde los archivos CSV...")
    params = cargar_parametros(
        csv_pseudo=CSV_PSEUDO,
        csv_rechazo=CSV_RECHAZO,
        csv_inversa=CSV_INVERSA,
        csv_historico=CSV_HISTORICO
    )
    
    # 2. Imprimir los parámetros detectados
    imprimir_parametros(params)

    # 3. Ejecutar simulación
    resultados = simular_actual(
        params=params,
        CEP=CEP,
        CVP=CVP,
        CALM=CALM,
        CSOB=CSOB,
        TF=TF,
        SMR=SMR,
        MAX_CAP=MAX_CAP,
        ST_0=ST_0,
        verbose=True
    )

    # 4. Pruebas estadísticas sobre los r generados durante la simulación
    gen_usado = resultados["gen"]
    print(f"Total de números pseudoaleatorios generados en simulación: {gen_usado.count}")
    
    if len(gen_usado.secuencia) >= 10:
        pruebas = PruebasEstadisticas(gen_usado.secuencia, alfa=ALFA)
        pruebas.ejecutar_todas(verbose=True)
    else:
        print("⚠️ No hay suficientes números pseudoaleatorios para ejecutar las pruebas estadísticas.")
