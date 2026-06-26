from Pruebas.GenNumsAleatorios import GeneradorCongruencial
from Generadores.Demanda import GeneradorDemanda
from Generadores.DiasDemora import GeneradorDemora


def simular_actual(
    params:   dict,
    CEP:      float = 0,
    CVP:      float = 0,
    CALM:     float = 0,
    CSOB:     float = 0,
    CUN:      float = 234_000,    # Costo de compra por unidad ($)
    CV:       float = 305_000,    # Precio de venta por unidad ($)
    PRESUP_0: float = 1_000_000,  # Presupuesto inicial ($)
    TF:       int   = 70,
    MAX_CAP:  int   = 10,
    ST_0:     int   = 7,
    verbose:  bool  = True,
    gen_compartido = None,
) -> dict:
    """
    Simula la política ACTUAL de gestión de inventario del Mueble Camilo.

    Nuevo diagrama de flujo (actualizado):
      · Días de CORRIDO: sábado (T%7=5) y domingo (T%7=6) no son hábiles → VD=0, sin actividad.
      · Pedido SOLO los lunes (T mod 7 == 0), siempre, sin importar pedidos pendientes.
      · TP = floor(MAX_CAP − ST)  ← determinístico, llena hasta capacidad máxima.
             (fórmula del diagrama: REDOND(IDE MOD CUN) = IDE dado que IDE < CUN siempre)
      · Sobrante detectado DESPUÉS de atender demanda: si ST > MAX_CAP → SOB = ST − MAX_CAP.
      · CTALM: si sobrante → cobra CALM sobre (ST−MAX_CAP); si no → cobra sobre ST.
      · PRESUP: ledger que suma ingresos por ventas y resta costos de compra y almacenamiento.

    Retorna dict con CTF, CTALM, CVTAP, CTEP, CALMSOB, VTAP, NROP, PRESUP, historial.
    """

    # ── Instanciar generadores ────────────────────────────────────────────────
    pc  = params["params_cong"]
    pr  = params["params_rechazo"]
    pu  = params["params_uniforme"]

    if gen_compartido is not None:
        gen = gen_compartido
    else:
        gen = GeneradorCongruencial(pc["X0"], pc["a"], pc["c"], pc["m"])

    gen_demanda = GeneradorDemanda(gen, pr["lam"], pr["a_rej"], pr["b_rej"], pr["m_rej"])
    gen_demora  = GeneradorDemora(gen, pu["DE_MIN"], pu["DE_MAX"])

    # ── Estado inicial ────────────────────────────────────────────────────────
    T       = -1  # DIA INICIAL se pone -1 porque en el primer ciclo de while se suma 1 antes de evaluar las condiciones donde 0 corresponde a dia Lunes
    ST      = ST_0
    FLL     = {}    # {nrop: día_llegada}
    TP_lst  = {}    # {nrop: cantidad_pedida}

    CTALM   = 0.0
    CVTAP   = 0.0
    CTEP    = 0.0
    CALMSOB = 0.0
    VTAP    = 0
    NROP    = 0
    PRESUP  = PRESUP_0
    historial: list[dict] = []

    DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    # ── Tabla de salida ───────────────────────────────────────────────────────
    SEP = "─" * 140
    if verbose:
        print(f"\n{'=' * 140}")
        print("  SIMULACIÓN — SITUACIÓN ACTUAL  |  Mueble Camilo  |  S&M")
        print(f"{'=' * 140}")
        print(f"  TF={TF} días corridos | ST₀={ST_0} | MAX_CAP={MAX_CAP}")
        print(f"  CEP=${CEP} | CVP=${CVP} | CALM=${CALM} | CSOB=${CSOB}")
        print(f"  CUN=${CUN:,.0f} | CV=${CV:,.0f} | PRESUP₀=${PRESUP_0:,.0f}")
        print(f"  Rechazo: λ={pr['lam']} a={pr['a_rej']} b={pr['b_rej']} M={pr['m_rej']}"
              f"  |  Demora: Unif({pu['DE_MIN']},{pu['DE_MAX']}) días corridos")
        print(SEP)
        print(
            f"{'T':>4} | {'Día':>5} | {'VD':>3} | {'ST_ini':>6} | {'ST_fin':>6} | "
            f"{'SOB':>4} | {'VTAP_d':>6} | {'Evento':<42} | "
            f"{'CTALM':>9} | {'CVTAP':>9} | {'CTEP':>7} | {'CALMSOB':>9} | {'PRESUP':>13}"
        )
        print(SEP)

    # ── Loop principal ────────────────────────────────────────────────────────
    while True:
        T += 1

        # Determinar día de la semana (0=Lun … 4=Vie → hábil | 5=Sáb, 6=Dom → no hábil)
        dia_semana  = T % 7
        dia_nombre  = DIAS[dia_semana]
        DIA_HABIL   = dia_semana <= 4   # Lunes a Viernes

        # ── Fin de semana: sin actividad comercial ────────────────────────────
        if not DIA_HABIL:
            historial.append({
                "T": T, "dia": dia_nombre, "VD": 0, "ST_ini": ST, "ST": ST,
                "SOB": 0, "VTAP_dia": 0, "NROP": NROP,
                "CTALM": CTALM, "CVTAP": CVTAP, "CTEP": CTEP, "CALMSOB": CALMSOB,
                "PRESUP": PRESUP, "pedido": None, "llegadas": [],
            })
            if verbose:
                print(
                    f"{T:>4} | {dia_nombre:>5} | {'---':>3} | {ST:>6} | {ST:>6} | "
                    f"{'---':>4} | {'---':>6} | {'[No hábil — fin de semana]':<42} | "
                    f"{'---':>9} | {'---':>9} | {'---':>7} | {'---':>9} | {PRESUP:>13,.0f}"
                )
            if T >= TF:
                break
            continue

        ST_ini = ST

        # [1] Recepciones del día — busca si algún pedido llega hoy
        SOB      = 0
        llegadas = [k for k, d in FLL.items() if T == d]
        for k in llegadas:
            cant_recibida = TP_lst.pop(k)
            ST += cant_recibida   # puede exceder MAX_CAP; el sobrante se calcula DESPUÉS de VD
            FLL.pop(k)

        # [2] Demanda del día (método de rechazo → Poisson)
        VD = gen_demanda.siguiente()

        # [3] Atender demanda, calcular PRESUP e identificar sobrante post-demanda
        vtap_dia = 0
        if ST >= VD:
            ST     -= VD
            PRESUP += VD * CV               # ingreso por venta completa

            # Verificar sobrante LUEGO de atender demanda
            if ST > MAX_CAP:
                SOB     = ST - MAX_CAP
                # CTALM cobra sobre el excedente (unidades sobrantes) a tasa CALM
                CTALM  += (ST - MAX_CAP) * CALM
                PRESUP -= (ST - MAX_CAP) * CALM
            else:
                SOB     = 0
                CTALM  += ST * CALM         # cobra sobre stock restante
                PRESUP -= ST * CALM
        else:
            # Stock insuficiente: venta parcial + ventas perdidas
            vtap_dia = VD - ST
            VTAP    += vtap_dia
            PRESUP  += ST * CV              # ingreso solo por lo que pudo vender
            CVTAP   += vtap_dia * CVP
            ST       = 0
            SOB      = 0

        # [4] Costo almacenamiento sobrante (siempre, aunque SOB=0 no suma nada)
        CALMSOB += SOB * CSOB
        PRESUP  -= SOB * CSOB

        # [5] ¿Es lunes? → emitir pedido (siempre, independientemente de pendientes)
        pedido_info = None
        if T % 7 == 0:                      # Lunes
            IDE = MAX_CAP - ST              # unidades para llenar hasta capacidad
            if IDE > 0:
                # Paso 1: TP = TRUNC(PRESUP / CUN) — cuánto puedo comprar con el presupuesto
                TP_nuevo = int(PRESUP / CUN)

                # Paso 2 (loop del diagrama): mientras TP supere el ideal, reducir de a 1
                # → garantiza que no compramos más de lo que cabe (TP <= IDE)
                while TP_nuevo > IDE:
                    TP_nuevo -= 1

                # Solo emitir pedido si se puede comprar al menos 1 unidad
                if TP_nuevo > 0:
                    PRESUP   -= TP_nuevo * CUN  # egreso por compra
                    NROP     += 1
                    TP_lst[NROP] = TP_nuevo
                    CTEP     += CEP
                    DE        = gen_demora.siguiente()
                    FLL[NROP] = T + DE
                    pedido_info = {"nrop": NROP, "tp": TP_nuevo, "de": DE, "fll": T + DE}

        # Registro
        historial.append({
            "T": T, "dia": dia_nombre, "VD": VD, "ST_ini": ST_ini, "ST": ST,
            "SOB": SOB, "VTAP_dia": vtap_dia, "NROP": NROP,
            "CTALM": CTALM, "CVTAP": CVTAP, "CTEP": CTEP, "CALMSOB": CALMSOB,
            "PRESUP": PRESUP, "pedido": pedido_info, "llegadas": llegadas,
        })

        if verbose:
            evt = ""
            if llegadas:
                evt += f"[llegó #{llegadas}] "
            if pedido_info:
                p    = pedido_info
                evt += f"→ Ped.#{p['nrop']:02d}: {p['tp']}u DE={p['de']}d arr.T={p['fll']}"
            print(
                f"{T:>4} | {dia_nombre:>5} | {VD:>3} | {ST_ini:>6} | {ST:>6} | "
                f"{SOB:>4} | {vtap_dia:>6} | {evt:<42} | "
                f"{CTALM:>9.2f} | {CVTAP:>9.2f} | {CTEP:>7.2f} | {CALMSOB:>9.2f} | {PRESUP:>13,.0f}"
            )

        if T >= TF:
            break

    # ── Resultados finales ────────────────────────────────────────────────────
    CTF = CTALM + CVTAP + CTEP + CALMSOB

    if verbose:
        print(SEP)
        print(f"\n{'=' * 65}")
        print("  📊  RESULTADOS FINALES — SITUACIÓN ACTUAL")
        print(f"{'=' * 65}")
        print(f"  CTALM   (almacenamiento regular)  : $ {CTALM:>12.2f}")
        print(f"  CVTAP   (ventas perdidas)          : $ {CVTAP:>12.2f}")
        print(f"  CTEP    (emisión de pedidos)       : $ {CTEP:>12.2f}")
        print(f"  CALMSOB (almacenamiento sobrante)  : $ {CALMSOB:>12.2f}")
        print(f"  {'─' * 55}")
        print(f"  CTF     (costo total)              : $ {CTF:>12.2f}")
        print(f"\n  PRESUP  (presupuesto final)        : $ {PRESUP:>12,.0f}")
        print(f"  VTAP    (unidades perdidas)        :   {VTAP:>5}")
        print(f"  NROP    (pedidos realizados)       :   {NROP:>5}")
        print(f"  Números generados                  :   {gen.count:>5}")
        print(f"  Intentos método de rechazo         :   {gen_demanda.intentos:>5}")
        print(f"  Demandas aceptadas                 :   {gen_demanda.aceptados:>5}")
        print(f"{'=' * 65}\n")

    return {
        "CTF": CTF, "CTALM": CTALM, "CVTAP": CVTAP,
        "CTEP": CTEP, "CALMSOB": CALMSOB,
        "VTAP": VTAP, "NROP": NROP, "PRESUP": PRESUP,
        "historial": historial,
        "gen": gen,
    }
