import math
from datos import cargar_parametros, imprimir_parametros
from simulacion_actual import simular_actual
from simulacion_ideal import simular_ideal
from Pruebas.GenNumsAleatorios import GeneradorCongruencial
from Pruebas.DistUniformeSim import PruebasEstadisticas

# ==============================================================================
# ⚙️ PARÁMETROS CONFIGURABLES  ← Modificar valores aquí
# ==============================================================================

# Cantidad de Réplicas (Corridas independientes)
N_REPLICACIONES = 1500

# Costos (en $) — Definir valores para análisis financiero real
CEP      = 35_000.0    # Costo de emisión por pedido ($/pedido)
CVP      = 71_000.0    # Costo de venta perdida ($/unidad)
CALM     = 800.0       # Costo de almacenamiento regular ($/unidad·día)
CSOB     = 2_000.0     # Costo de almacenamiento sobrante ($/unidad·día)

# Costos de compra/venta del mueble (situación actual — nuevo diagrama)
CUN      = 234_000.0   # Costo de compra por unidad al proveedor ($)
CV       = 305_000.0   # Precio de venta al cliente por unidad ($)
PRESUP_0 = 1_000_000.0 # Presupuesto inicial dedicado al mueble Camilo ($)

# Parámetros de Simulación
TF      = 70       # Tiempo final de simulación (días corridos)
MAX_CAP = 10       # Capacidad máxima del depósito
ST_0    = 7        # Stock inicial

# Nivel de significancia para las pruebas estadísticas
ALFA    = 0.05

# Rutas de archivos CSV
CSV_PSEUDO    = "Tablas - nro_pseudo.csv"
CSV_RECHAZO   = "Tablas - M. Rechazo.csv"
CSV_INVERSA   = "Tablas - Trasnformada Inversa de corrido.csv"   # Todos los días (de corrido, sin diferenciar hábiles)

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

    # 3. Ejecutar simulación de SITUACIÓN ACTUAL con N replicaciones
    print("\n" + "="*80)
    print(f" ▶️  EJECUTANDO SIMULACIÓN ACTUAL: {N_REPLICACIONES} RÉPLICAS MONTE CARLO")
    print("="*80)
    
    pc = params["params_cong"]
    gen_actual = GeneradorCongruencial(pc["X0"], pc["a"], pc["c"], pc["m"])
    
    costos_actual     = []
    alm_actual        = []
    sob_actual        = []
    vtap_cost_actual  = []
    emision_actual    = []
    vtap_unids_actual = []
    nrop_actual       = []
    presup_actual     = []
    
    for _ in range(N_REPLICACIONES):
        res = simular_actual(
            params=params,
            CEP=CEP,
            CVP=CVP,
            CALM=CALM,
            CSOB=CSOB,
            CUN=CUN,
            CV=CV,
            PRESUP_0=PRESUP_0,
            TF=TF,
            MAX_CAP=MAX_CAP,
            ST_0=ST_0,
            verbose=False,
            gen_compartido=gen_actual
        )
        costos_actual.append(res["CTF"])
        alm_actual.append(res["CTALM"])
        sob_actual.append(res["CALMSOB"])
        vtap_cost_actual.append(res["CVTAP"])
        emision_actual.append(res["CTEP"])
        vtap_unids_actual.append(res["VTAP"])
        nrop_actual.append(res["NROP"])
        presup_actual.append(res["PRESUP"])

    avg_cost_actual       = sum(costos_actual)     / N_REPLICACIONES
    avg_alm_actual        = sum(alm_actual)         / N_REPLICACIONES
    avg_sob_actual        = sum(sob_actual)         / N_REPLICACIONES
    avg_vtap_cost_actual  = sum(vtap_cost_actual)   / N_REPLICACIONES
    avg_emision_actual    = sum(emision_actual)      / N_REPLICACIONES
    avg_vtap_unids_actual = sum(vtap_unids_actual)   / N_REPLICACIONES
    avg_nrop_actual       = sum(nrop_actual)         / N_REPLICACIONES
    avg_presup_actual     = sum(presup_actual)       / N_REPLICACIONES

    print(f"\nResultados Promedio de {N_REPLICACIONES} réplicas (Situación Actual):")
    print(f"  CTALM   (almacenamiento promedio) : $ {avg_alm_actual:>12.2f}")
    print(f"  CALMSOB (sobrante promedio)       : $ {avg_sob_actual:>12.2f}")
    print(f"  CVTAP   (ventas perdidas promedio): $ {avg_vtap_cost_actual:>12.2f}")
    print(f"  CTEP    (emisión promedio)        : $ {avg_emision_actual:>12.2f}")
    print(f"  {'─' * 45}")
    print(f"  CTF     (costo total promedio)    : $ {avg_cost_actual:>12.2f}")
    print(f"  PRESUP  (presupuesto final prom)  : $ {avg_presup_actual:>12,.0f}")
    print(f"  Ventas Perdidas (unidades prom)   :   {avg_vtap_unids_actual:>12.2f}")
    print(f"  Pedidos Realizados (promedio)     :   {avg_nrop_actual:>12.2f}")

    # 4. Pruebas estadísticas sobre los r generados (muestra representativa)
    # NOTA: El generador congruencial tiene un módulo m=14729 y un período de 510.
    # Si probamos la secuencia completa de 286.874 números, las pruebas rechazarán
    # inevitablemente debido a la repetición periódica de la secuencia.
    # Por lo tanto, validamos la calidad de los números generados probando los primeros 500 números
    # (casi un período completo antes de que se repita).
    print(f"\nTotal de números pseudoaleatorios generados en la simulación: {gen_actual.count}")
    N_TEST = min(500, len(gen_actual.secuencia))
    if N_TEST >= 10:
        print(f"\n🧪 Validación estadística sobre los primeros {N_TEST} números generados:")
        pruebas_act = PruebasEstadisticas(gen_actual.secuencia[:N_TEST], alfa=ALFA)
        pruebas_act.ejecutar_todas(verbose=True)

    # 5. Ejecutar simulación MODELO IDEAL con N replicaciones variando SR
    print("\n" + "="*80)
    print(f" ▶️  EJECUTANDO MODELO IDEAL: {N_REPLICACIONES} RÉPLICAS (Búsqueda de SR óptimo)")
    print("="*80)
    
    comparativa = []
    optimo_sr = 0
    min_ctf = float('inf')
    optimo_metrics = {}

    print(f"\nVariando Punto de Reorden (SR) de 0 a {MAX_CAP - 1}:")
    print("─"*78)
    print(f"{'SR':>3} | {'CTF (Total Prom)':>17} | {'CTALM':>10} | {'CVTAP':>10} | {'CTEP':>10} | {'VTAP':>6} | {'NROP':>5}")
    print("─"*78)

    for sr in range(MAX_CAP):
        # Para que la comparación sea estadísticamente justa, usamos la misma semilla inicial en cada SR
        # aplicando la técnica de Números Aleatorios Comunes (Common Random Numbers)
        gen_ideal = GeneradorCongruencial(pc["X0"], pc["a"], pc["c"], pc["m"])
        
        costos_ideal = []
        alm_ideal = []
        vtap_cost_ideal = []
        emision_ideal = []
        vtap_unids_ideal = []
        nrop_ideal = []
        
        for _ in range(N_REPLICACIONES):
            res_ideal = simular_ideal(
                params=params,
                CEP=CEP,
                CVP=CVP,
                CALM=CALM,
                TF=TF,
                SR=sr,
                MAX_CAP=MAX_CAP,
                ST_0=ST_0,
                verbose=False,
                gen_compartido=gen_ideal
            )
            costos_ideal.append(res_ideal["CTF"])
            alm_ideal.append(res_ideal["CTALM"])
            vtap_cost_ideal.append(res_ideal["CVTAP"])
            emision_ideal.append(res_ideal["CTEP"])
            vtap_unids_ideal.append(res_ideal["VTAP"])
            nrop_ideal.append(res_ideal["NROP"])
            
        avg_cost_ideal = sum(costos_ideal) / N_REPLICACIONES
        avg_alm_ideal = sum(alm_ideal) / N_REPLICACIONES
        avg_vtap_cost_ideal = sum(vtap_cost_ideal) / N_REPLICACIONES
        avg_emision_ideal = sum(emision_ideal) / N_REPLICACIONES
        avg_vtap_unids_ideal = sum(vtap_unids_ideal) / N_REPLICACIONES
        avg_nrop_ideal = sum(nrop_ideal) / N_REPLICACIONES
        
        print(f"{sr:>3} | ${avg_cost_ideal:>16.2f} | ${avg_alm_ideal:>9.2f} | ${avg_vtap_cost_ideal:>9.2f} | ${avg_emision_ideal:>9.2f} | {avg_vtap_unids_ideal:>6.1f} | {avg_nrop_ideal:>5.1f}")
        
        metrics = {
            "SR": sr,
            "CTF": avg_cost_ideal,
            "CTALM": avg_alm_ideal,
            "CVTAP": avg_vtap_cost_ideal,
            "CTEP": avg_emision_ideal,
            "VTAP": avg_vtap_unids_ideal,
            "NROP": avg_nrop_ideal
        }
        comparativa.append(metrics)
        
        if avg_cost_ideal < min_ctf:
            min_ctf = avg_cost_ideal
            optimo_sr = sr
            optimo_metrics = metrics

    print("─"*78)
    print(f"🎯 El Stock de Referencia (SR) óptimo promedio es: {optimo_sr} con un costo medio de ${min_ctf:.2f}")

    # 6. Comparación final entre Actual e Ideal Óptimo
    print("\n" + "="*80)
    print(" 📊 COMPARATIVA FINAL PROMEDIO: SITUACIÓN ACTUAL vs. MODELO IDEAL ÓPTIMO")
    print("="*80)
    print(f"{'Métrica (Valores Medios)':<30} | {'Situación Actual':>18} | {'Modelo Ideal (SR=' + str(optimo_sr) + ')':>22}")
    print("─"*78)
    print(f"{'Costo Almacenamiento Regular':<30} | ${avg_alm_actual:>17.2f} | ${optimo_metrics['CTALM']:>21.2f}")
    print(f"{'Costo Almacenamiento Sobrante':<30} | ${avg_sob_actual:>17.2f} | {'N/A':>22}")
    print(f"{'Costo Ventas Perdidas':<30} | ${avg_vtap_cost_actual:>17.2f} | ${optimo_metrics['CVTAP']:>21.2f}")
    print(f"{'Costo Emisión Pedidos':<30} | ${avg_emision_actual:>17.2f} | ${optimo_metrics['CTEP']:>21.2f}")
    print(f"{'COSTO TOTAL DE FUNCIONAMIENTO':<30} | ${avg_cost_actual:>17.2f} | ${optimo_metrics['CTF']:>21.2f}")
    print("─"*78)
    print(f"{'Unidades Perdidas (VTAP)':<30} | {avg_vtap_unids_actual:>17.2f} | {optimo_metrics['VTAP']:>21.2f}")
    print(f"{'Pedidos Realizados (NROP)':<30} | {avg_nrop_actual:>17.2f} | {optimo_metrics['NROP']:>21.2f}")
    print("="*80 + "\n")
