from Pruebas import DistUniformeSim
import math
from datos import cargar_parametros, imprimir_parametros
from simulacion_actual import simular_actual
from simulacion_ideal import simular_ideal
from Pruebas.GenNumsAleatorios import GeneradorCongruencial
from Pruebas.DistUniformeSim import PruebasEstadisticas
from graficas import generar_graficas_actual

# ==============================================================================
# ⚙️ PARÁMETROS CONFIGURABLES  ← Modificar valores aquí
# ==============================================================================

# Cantidad de Réplicas (Corridas independientes)
N_REPLICACIONES = 1500

# Costos (en $) — Definir valores para análisis financiero real
CEP      = 65_000.0    # Costo de emisión por pedido ($/pedido)
CVP      = 93_600.0    # Costo de venta perdida ($/unidad)
CALM     = 3_000.0       # Costo de almacenamiento regular ($/unidad·día)
CSOB     = 30_000.0     # Costo de almacenamiento sobrante ($/unidad·día)

# Costos de compra/venta del mueble (situación actual — nuevo diagrama)
CUN      = 234_000.0   # Costo de compra por unidad al proveedor ($)
CV       = 327_600.0   # Precio de venta al cliente por unidad ($)
PRESUP_0 = 800_000.0 # Presupuesto inicial dedicado al mueble Camilo ($)

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
    rng_counts        = []   # números pseudoaleatorios por réplica
    
    for _ in range(N_REPLICACIONES):
        _cnt_antes = gen_actual.count
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
        rng_counts.append(gen_actual.count - _cnt_antes)
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
    avg_rng_actual        = sum(rng_counts)          / N_REPLICACIONES

    # ── Resultados Financieros y Operativos ──────────────────────────────────
    _L = 46   # ancho columna etiqueta
    _V = 22   # ancho columna valor
    _W = _L + _V + 6   # ancho interior total

    def _fila(label, valor_str):
        return f"║  {label:<{_L}}{valor_str:>{_V}}  ║"

    def _sep(char="─"):
        return f"║  {char * (_W - 2)}  ║"

    print()
    print(f"╔{'═' * _W}╗")
    encabezado = f"📊  RESULTADOS — SITUACIÓN ACTUAL   ({N_REPLICACIONES} réplicas · TF={TF} días)"
    print(f"║  {encabezado:<{_W - 2}}║")
    print(f"╠{'═' * _W}╣")

    # Costos
    print(f"║  {'── COSTOS DE INVENTARIO':<{_W - 2}}║")
    print(_sep())
    print(_fila("Concepto", "Promedio ($)"))
    print(_sep())
    print(_fila("Almacenamiento Regular       (CTALM)",  f"$ {avg_alm_actual:>15,.2f}"))
    print(_fila("Almacenamiento Sobrante      (CALMSOB)", f"$ {avg_sob_actual:>15,.2f}"))
    print(_fila("Emisión de Pedidos           (CTEP)",   f"$ {avg_emision_actual:>15,.2f}"))
    print(_fila("Ventas Perdidas              (CVTAP)",  f"$ {avg_vtap_cost_actual:>15,.2f}"))
    print(_sep("─"))
    print(_fila("💰 COSTO TOTAL DE FUNCIONAMIENTO (CTF)", f"$ {avg_cost_actual:>15,.2f}"))

    # Operativos
    print(f"╠{'═' * _W}╣")
    print(f"║  {'── INDICADORES OPERATIVOS':<{_W - 2}}║")
    print(_sep())
    print(_fila("Concepto", "Valor"))
    print(_sep())
    print(_fila("Presupuesto Final Promedio   (Caja)",  f"$ {avg_presup_actual:>15,.2f}"))
    print(_fila("Demanda Insatisfecha Prom.   (VTAP)",  f"{avg_vtap_unids_actual:>14.1f} u"))
    print(_fila("Pedidos Realizados Prom.     (NROP)",  f"{avg_nrop_actual:>12.1f} ped."))
    print(_fila("Números Pseudoaleatorios     (RNG)",   f"{avg_rng_actual:>12.1f} /rep."))
    print(f"╚{'═' * _W}╝")

    # 4. Pruebas estadísticas sobre los r generados (muestra representativa de N=220)
    N_TEST = min(220, len(gen_actual.secuencia))
    if N_TEST >= 10:
        pruebas_act = PruebasEstadisticas(gen_actual.secuencia[:N_TEST], alfa=ALFA)
        res_pruebas = pruebas_act.ejecutar_todas(verbose=False)
        
        print("\n┌────────────────────────────────────────────────────────────────────────┐")
        print(f"│   🧪  VERIFICACIÓN Y VALIDACIÓN DEL GENERADOR (N = {N_TEST} NÚMEROS)        │")
        print("├────────────────────────────────────────────────────────────────────────┤")
        print("│  ¿Por qué probamos una muestra de N=220 en lugar de todos (286.874)?    │")
        print("│  • El generador congruencial de la cátedra (m=14729) tiene un período  │")
        print("│    de 510. Si probáramos toda la corrida, la repetición cíclica        │")
        print("│    haría fallar las pruebas de independencia por predictibilidad.      │")
        print("│  • Se valida una muestra fija de N=220 para certificar estadísticamente│")
        print("│    la calidad y uniformidad del generador (igual que en el Excel).     │")
        print("├────────────────────────────────────────────────────────────────────────┤")
        print("│  Resultados de las Pruebas (Significancia α = 0.05):                   │")
        
        def fmt_res(val):
            return "✅ APRUEBA" if val else "❌ RECHAZA"
            
        print(f"│    1. Prueba de Media                           : {fmt_res(res_pruebas['media']):<14} │")
        print(f"│    2. Prueba de Varianza                        : {fmt_res(res_pruebas['varianza']):<14} │")
        print(f"│    3. Prueba de Uniformidad (χ²)                : {fmt_res(res_pruebas['uniformidad']):<14} │")
        print(f"│    4. Prueba de Independencia (Corrida ↑↓)      : {fmt_res(res_pruebas['corrida_ud']):<14} │")
        print(f"│    5. Prueba de Independencia (Corrida de Media): {fmt_res(res_pruebas['corrida_media']):<14} │")
        print("├────────────────────────────────────────────────────────────────────────┤")
        
        aprobadas = sum(1 for v in res_pruebas.values() if v)
        if aprobadas == 5:
            print("│  🎉 CONCLUSIÓN GLOBAL: 5/5 pruebas aprobadas                            │")
            print("│  La secuencia es estadísticamente uniforme e independiente.            │")
        else:
            print(f"│  ⚠️  CONCLUSIÓN GLOBAL: {aprobadas}/5 pruebas aprobadas                          │")
            print("│  La secuencia NO supera todas las pruebas de aleatoriedad.             │")
        print("└────────────────────────────────────────────────────────────────────────┘\n")

    # 5. Generar gráficas de análisis de la Situación Actual
    print("\n" + "="*80)
    print(" 📊  GENERANDO GRÁFICAS DE ANÁLISIS — SITUACIÓN ACTUAL")
    print("="*80)
    generar_graficas_actual(
        costos_actual    = costos_actual,
        alm_actual       = alm_actual,
        sob_actual       = sob_actual,
        vtap_cost_actual = vtap_cost_actual,
        emision_actual   = emision_actual,
        N_REPLICACIONES  = N_REPLICACIONES,
        TF               = TF,
        alfa             = ALFA,
        guardar          = True,
        nombre_archivo   = "graficas_situacion_actual.png",
    )

    # 6. Ejecutar simulación MODELO IDEAL con N replicaciones variando SR
    # print("\n" + "="*80)
    # print(f" ▶️  EJECUTANDO MODELO IDEAL: {N_REPLICACIONES} RÉPLICAS (Búsqueda de SR óptimo)")
    # print("="*80)
    # 
    # comparativa = []
    # optimo_sr = 0
    # min_ctf = float('inf')
    # optimo_metrics = {}
    # 
    # print(f"\nVariando Punto de Reorden (SR) de 0 a {MAX_CAP - 1}:")
    # print("─"*78)
    # print(f"{'SR':>3} | {'CTF (Total Prom)':>17} | {'CTALM':>10} | {'CVTAP':>10} | {'CTEP':>10} | {'VTAP':>6} | {'NROP':>5}")
    # print("─"*78)
    # 
    # for sr in range(MAX_CAP):
    #     # Para que la comparación sea estadísticamente justa, usamos la misma semilla inicial en cada SR
    #     # aplicando la técnica de Números Aleatorios Comunes (Common Random Numbers)
    #     gen_ideal = GeneradorCongruencial(pc["X0"], pc["a"], pc["c"], pc["m"])
    #     
    #     costos_ideal = []
    #     alm_ideal = []
    #     vtap_cost_ideal = []
    #     emision_ideal = []
    #     vtap_unids_ideal = []
    #     nrop_ideal = []
    #     
    #     for _ in range(N_REPLICACIONES):
    #         res_ideal = simular_ideal(
    #             params=params,
    #             CEP=CEP,
    #             CVP=CVP,
    #             CALM=CALM,
    #             TF=TF,
    #             SR=sr,
    #             MAX_CAP=MAX_CAP,
    #             ST_0=ST_0,
    #             verbose=False,
    #             gen_compartido=gen_ideal
    #         )
    #         costos_ideal.append(res_ideal["CTF"])
    #         alm_ideal.append(res_ideal["CTALM"])
    #         vtap_cost_ideal.append(res_ideal["CVTAP"])
    #         emision_ideal.append(res_ideal["CTEP"])
    #         vtap_unids_ideal.append(res_ideal["VTAP"])
    #         nrop_ideal.append(res_ideal["NROP"])
    #         
    #     avg_cost_ideal = sum(costos_ideal) / N_REPLICACIONES
    #     avg_alm_ideal = sum(alm_ideal) / N_REPLICACIONES
    #     avg_vtap_cost_ideal = sum(vtap_cost_ideal) / N_REPLICACIONES
    #     avg_emision_ideal = sum(emision_ideal) / N_REPLICACIONES
    #     avg_vtap_unids_ideal = sum(vtap_unids_ideal) / N_REPLICACIONES
    #     avg_nrop_ideal = sum(nrop_ideal) / N_REPLICACIONES
    #     
    #     print(f"{sr:>3} | ${avg_cost_ideal:>16.2f} | ${avg_alm_ideal:>9.2f} | ${avg_vtap_cost_ideal:>9.2f} | ${avg_emision_ideal:>9.2f} | {avg_vtap_unids_ideal:>6.1f} | {avg_nrop_ideal:>5.1f}")
    #     
    #     metrics = {
    #         "SR": sr,
    #         "CTF": avg_cost_ideal,
    #         "CTALM": avg_alm_ideal,
    #         "CVTAP": avg_vtap_cost_ideal,
    #         "CTEP": avg_emision_ideal,
    #         "VTAP": avg_vtap_unids_ideal,
    #         "NROP": avg_nrop_ideal
    #     }
    #     comparativa.append(metrics)
    #     
    #     if avg_cost_ideal < min_ctf:
    #         min_ctf = avg_cost_ideal
    #         optimo_sr = sr
    #         optimo_metrics = metrics
    # 
    # print("─"*78)
    # print(f"🎯 El Stock de Referencia (SR) óptimo promedio es: {optimo_sr} con un costo medio de ${min_ctf:.2f}")
    # 
    # # 6. Comparación final entre Actual e Ideal Óptimo
    # print("\n" + "="*80)
    # print(" 📊 COMPARATIVA FINAL PROMEDIO: SITUACIÓN ACTUAL vs. MODELO IDEAL ÓPTIMO")
    # print("="*80)
    # print(f"{'Métrica (Valores Medios)':<30} | {'Situación Actual':>18} | {'Modelo Ideal (SR=' + str(optimo_sr) + ')':>22}")
    # print("─"*78)
    # print(f"{'Costo Almacenamiento Regular':<30} | ${avg_alm_actual:>17.2f} | ${optimo_metrics['CTALM']:>21.2f}")
    # print(f"{'Costo Almacenamiento Sobrante':<30} | ${avg_sob_actual:>17.2f} | {'N/A':>22}")
    # print(f"{'Costo Ventas Perdidas':<30} | ${avg_vtap_cost_actual:>17.2f} | ${optimo_metrics['CVTAP']:>21.2f}")
    # print(f"{'Costo Emisión Pedidos':<30} | ${avg_emision_actual:>17.2f} | ${optimo_metrics['CTEP']:>21.2f}")
    # print(f"{'COSTO TOTAL DE FUNCIONAMIENTO':<30} | ${avg_cost_actual:>17.2f} | ${optimo_metrics['CTF']:>21.2f}")
    # print("─"*78)
    # print(f"{'Unidades Perdidas (VTAP)':<30} | {avg_vtap_unids_actual:>17.2f} | {optimo_metrics['VTAP']:>21.2f}")
    # print(f"{'Pedidos Realizados (NROP)':<30} | {avg_nrop_actual:>17.2f} | {optimo_metrics['NROP']:>21.2f}")
    # print("="*80 + "\n")
