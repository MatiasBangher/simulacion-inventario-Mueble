from Pruebas.GenNumsAleatorios import GeneradorCongruencial
from Generadores.Demanda import GeneradorDemanda
from Generadores.DiasDemora import GeneradorDemora


def simular_actual(
    params:  dict,
    CEP:     float = 0,
    CVP:     float = 0,
    CALM:    float = 0,
    CSOB:    float = 0,
    TF:      int   = 70,
    SMR:     int   = 10,
    MAX_CAP: int   = 10,
    ST_0:    int   = 7,
    verbose: bool  = True,
    gen_compartido = None,
) -> dict:
    """
    Simula la política ACTUAL de gestión de inventario del Mueble Camilo.

    Política:
      · Pedido solo los lunes (T mod 7 == 0)
      · TP = Aleatorio(1, SMR−ST)  — "a ojo", generado con el método congruencial
      · Múltiples pedidos en tránsito simultáneos (FLL y TP_lst son dicts)
      · Sobrantes: si ST > MAX_CAP tras recibir mercadería → costo adicional

    Retorna dict con CTF, CTALM, CVTAP, CTEP, CALMSOB, VTAP, NROP, historial.
    """

    # ── Instanciar generadores (un único gen congruencial compartido) ─────────
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
    T       = -1
    ST      = ST_0
    FLL     = {}    # {nrop: día_llegada}
    TP_lst  = {}    # {nrop: cantidad}

    CTALM   = 0.0
    CVTAP   = 0.0
    CTEP    = 0.0
    CALMSOB = 0.0
    VTAP    = 0
    NROP    = 0
    historial: list[dict] = []

    # ── Tabla de salida ───────────────────────────────────────────────────────
    SEP = "─" * 118
    if verbose:
        print(f"\n{'=' * 118}")
        print("  SIMULACIÓN — SITUACIÓN ACTUAL  |  Mueble Camilo  |  S&M")
        print(f"{'=' * 118}")
        print(f"  TF={TF} días | ST₀={ST_0} | SMR={SMR} | MAX_CAP={MAX_CAP}")
        print(f"  CEP=${CEP} | CVP=${CVP} | CALM=${CALM} | CSOB=${CSOB}")
        print(f"  Congruencial: X₀={pc['X0']} a={pc['a']} c={pc['c']} m={pc['m']}")
        print(f"  Rechazo: λ={pr['lam']} a={pr['a_rej']} b={pr['b_rej']} M={pr['m_rej']}"
              f"  |  Demora: Unif({pu['DE_MIN']},{pu['DE_MAX']})")
        print(SEP)
        print(
            f"{'T':>4} | {'VD':>3} | {'ST_ini':>6} | {'ST_fin':>6} | "
            f"{'SOB':>4} | {'VTAP_d':>6} | {'Evento':<40} | "
            f"{'CTALM':>9} | {'CVTAP':>9} | {'CTEP':>7} | {'CALMSOB':>9}"
        )
        print(SEP)

    # ── Loop principal ────────────────────────────────────────────────────────
    while True:
        T      += 1
        ST_ini  = ST

        # [2] Recepciones del día
        llegadas = [k for k, d in FLL.items() if T == d]
        SOB = 0
        for k in llegadas:
            cant_recibida = TP_lst.pop(k)
            if ST + cant_recibida > MAX_CAP:
                unidades_sobrantes = (ST + cant_recibida) - MAX_CAP
                SOB += unidades_sobrantes
                ST = MAX_CAP
            else:
                ST += cant_recibida
            FLL.pop(k)

        # [3] Demanda del día (método de rechazo)
        VD = gen_demanda.siguiente()

        # [4] Atender demanda
        vtap_dia = 0
        if ST >= VD:
            ST -= VD
            CTALM += ST * CALM
        else:
            vtap_dia = VD - ST
            VTAP    += vtap_dia
            CVTAP   += vtap_dia * CVP
            ST       = 0

        # [5] Costo sobrantes

        CALMSOB += SOB * CSOB

        # [6] ¿Es lunes? → revisar y emitir pedido "a ojo"
        pedido_info = None
        if T % 7 == 0:
            diff = SMR - ST
            if diff > 0:
                r_ojo    = gen.siguiente()
                TP_nuevo = max(1, min(diff, round(1 + (diff - 1) * r_ojo)))
                NROP    += 1
                TP_lst[NROP] = TP_nuevo
                CTEP    += CEP
                DE       = gen_demora.siguiente()
                FLL[NROP] = T + DE
                pedido_info = {"nrop": NROP, "tp": TP_nuevo, "de": DE, "fll": T + DE}

        # Registro
        historial.append({
            "T": T, "VD": VD, "ST_ini": ST_ini, "ST": ST,
            "SOB": SOB, "VTAP_dia": vtap_dia, "NROP": NROP,
            "CTALM": CTALM, "CVTAP": CVTAP, "CTEP": CTEP, "CALMSOB": CALMSOB,
            "pedido": pedido_info, "llegadas": llegadas,
        })

        if verbose:
            evt = ""
            if llegadas:
                evt += f"[llegó #{llegadas}] "
            if pedido_info:
                p    = pedido_info
                evt += f"→ Ped.#{p['nrop']:02d}: {p['tp']}u DE={p['de']} T={p['fll']}"
            print(
                f"{T:>4} | {VD:>3} | {ST_ini:>6} | {ST:>6} | "
                f"{SOB:>4} | {vtap_dia:>6} | {evt:<40} | "
                f"{CTALM:>9.2f} | {CVTAP:>9.2f} | {CTEP:>7.2f} | {CALMSOB:>9.2f}"
            )

        if T >= TF:
            break

    # ── Resultados finales ────────────────────────────────────────────────────
    CTF = CTALM + CVTAP + CTEP + CALMSOB

    if verbose:
        print(SEP)
        print(f"\n{'=' * 60}")
        print("  📊  RESULTADOS FINALES — SITUACIÓN ACTUAL")
        print(f"{'=' * 60}")
        print(f"  CTALM   (almacenamiento regular)  : $ {CTALM:>12.2f}")
        print(f"  CVTAP   (ventas perdidas)          : $ {CVTAP:>12.2f}")
        print(f"  CTEP    (emisión de pedidos)       : $ {CTEP:>12.2f}")
        print(f"  CALMSOB (almacenamiento sobrante)  : $ {CALMSOB:>12.2f}")
        print(f"  {'─' * 50}")
        print(f"  CTF     (costo total)              : $ {CTF:>12.2f}")
        print(f"\n  VTAP  (unidades perdidas)  :   {VTAP:>5}")
        print(f"  NROP  (pedidos realizados) :   {NROP:>5}")
        print(f"  Números generados          :   {gen.count:>5}")
        print(f"  Intentos método de rechazo :   {gen_demanda.intentos:>5}")
        print(f"  Demandas aceptadas         :   {gen_demanda.aceptados:>5}")
        print(f"{'=' * 60}\n")

    return {
        "CTF": CTF, "CTALM": CTALM, "CVTAP": CVTAP,
        "CTEP": CTEP, "CALMSOB": CALMSOB,
        "VTAP": VTAP, "NROP": NROP,
        "historial": historial,
        "gen": gen,   # expuesto para poder correr pruebas sobre los r generados
    }
