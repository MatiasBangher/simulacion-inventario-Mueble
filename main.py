from datos import cargar_parametros, imprimir_parametros
from simulacion_actual import simular_actual
from simulacion_ideal import simular_ideal
from Pruebas.DistUniformeSim import PruebasEstadisticas

# ==============================================================================
# ⚙️ PARÁMETROS CONFIGURABLES  ← Modificar valores aquí
# ==============================================================================

# Costos (en $) — Definir valores para análisis financiero real
CEP     = 100.0    # Costo de emisión por pedido ($/pedido)
CVP     = 250.0    # Costo de venta perdida ($/unidad)
CALM    = 2.0      # Costo de almacenamiento regular ($/unidad·día)
CSOB    = 5.0      # Costo de almacenamiento sobrante ($/unidad·día) (Solo Modelo Actual)

# Parámetros de Simulación
TF      = 70       # Tiempo final de simulación (días hábiles)
SMR     = 10       # Stock Medio de Referencia (situación actual)
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

    # 3. Ejecutar simulación de SITUACIÓN ACTUAL
    print("\n" + "="*80)
    print(" ▶️  EJECUTANDO SIMULACIÓN: SITUACIÓN ACTUAL")
    print("="*80)
    res_actual = simular_actual(
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

    # 4. Pruebas estadísticas sobre los r generados en Situación Actual
    gen_actual = res_actual["gen"]
    print(f"Total de números pseudoaleatorios generados en simulación actual: {gen_actual.count}")
    if len(gen_actual.secuencia) >= 10:
        print("\n🧪 Pruebas Estadísticas para la simulación Actual:")
        pruebas_act = PruebasEstadisticas(gen_actual.secuencia, alfa=ALFA)
        pruebas_act.ejecutar_todas(verbose=True)

    # 5. Ejecutar simulación MODELO IDEAL variando SR
    print("\n" + "="*80)
    print(" ▶️  EJECUTANDO SIMULACIÓN: MODELO IDEAL (Búsqueda de SR óptimo)")
    print("="*80)
    
    comparativa = []
    optimo_sr = 0
    min_ctf = float('inf')
    res_optimo = None

    print(f"\nVariando Punto de Reorden (SR) de 0 a {MAX_CAP - 1}:")
    print("─"*75)
    print(f"{'SR':>3} | {'CTF (Total)':>12} | {'CTALM':>10} | {'CVTAP':>10} | {'CTEP':>10} | {'VTAP':>6} | {'NROP':>5}")
    print("─"*75)

    for sr in range(MAX_CAP):
        # Corremos la simulación de forma silenciosa para la búsqueda
        res_ideal = simular_ideal(
            params=params,
            CEP=CEP,
            CVP=CVP,
            CALM=CALM,
            TF=TF,
            SR=sr,
            MAX_CAP=MAX_CAP,
            ST_0=ST_0,
            verbose=False
        )
        
        comparativa.append({
            "SR": sr,
            "CTF": res_ideal["CTF"],
            "CTALM": res_ideal["CTALM"],
            "CVTAP": res_ideal["CVTAP"],
            "CTEP": res_ideal["CTEP"],
            "VTAP": res_ideal["VTAP"],
            "NROP": res_ideal["NROP"]
        })
        
        print(f"{sr:>3} | ${res_ideal['CTF']:>11.2f} | ${res_ideal['CTALM']:>9.2f} | ${res_ideal['CVTAP']:>9.2f} | ${res_ideal['CTEP']:>9.2f} | {res_ideal['VTAP']:>6} | {res_ideal['NROP']:>5}")
        
        if res_ideal["CTF"] < min_ctf:
            min_ctf = res_ideal["CTF"]
            optimo_sr = sr
            res_optimo = res_ideal

    print("─"*75)
    print(f"🎯 El Stock de Referencia (SR) óptimo es: {optimo_sr} con un costo de ${min_ctf:.2f}")
    
    # 6. Mostrar el log detallado de la simulación del MODELO IDEAL óptimo
    print("\n" + "="*80)
    print(f" ▶️  DETALLE DIARIO DEL MODELO IDEAL ÓPTIMO (SR={optimo_sr})")
    print("="*80)
    
    # Corremos nuevamente pero con verbose=True para ver el reporte detallado
    simular_ideal(
        params=params,
        CEP=CEP,
        CVP=CVP,
        CALM=CALM,
        TF=TF,
        SR=optimo_sr,
        MAX_CAP=MAX_CAP,
        ST_0=ST_0,
        verbose=True
    )

    # 7. Comparación final entre Actual e Ideal Óptimo
    print("\n" + "="*80)
    print(" 📊 COMPARATIVA FINAL: SITUACIÓN ACTUAL vs. MODELO IDEAL ÓPTIMO")
    print("="*80)
    print(f"{'Métrica':<30} | {'Situación Actual':>18} | {'Modelo Ideal (SR=' + str(optimo_sr) + ')':>22}")
    print("─"*78)
    print(f"{'Costo Almacenamiento Regular':<30} | ${res_actual['CTALM']:>17.2f} | ${res_optimo['CTALM']:>21.2f}")
    print(f"{'Costo Almacenamiento Sobrante':<30} | ${res_actual['CALMSOB']:>17.2f} | {'N/A':>22}")
    print(f"{'Costo Ventas Perdidas':<30} | ${res_actual['CVTAP']:>17.2f} | ${res_optimo['CVTAP']:>21.2f}")
    print(f"{'Costo Emisión Pedidos':<30} | ${res_actual['CTEP']:>17.2f} | ${res_optimo['CTEP']:>21.2f}")
    print(f"{'COSTO TOTAL DE FUNCIONAMIENTO':<30} | ${res_actual['CTF']:>17.2f} | ${res_optimo['CTF']:>21.2f}")
    print("─"*78)
    print(f"{'Unidades Perdidas (VTAP)':<30} | {res_actual['VTAP']:>17} | {res_optimo['VTAP']:>21}")
    print(f"{'Pedidos Realizados (NROP)':<30} | {res_actual['NROP']:>17} | {res_optimo['NROP']:>21}")
    print("="*80 + "\n")
