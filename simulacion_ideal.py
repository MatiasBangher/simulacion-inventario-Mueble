from Pruebas.GenNumsAleatorios import GeneradorCongruencial
from Generadores.Demanda import GeneradorDemanda
from Generadores.DiasDemora import GeneradorDemora


def simular_ideal(
    params:  dict,
    CEP:     float = 0,
    CVP:     float = 0,
    CALM:    float = 0,
    TF:      int   = 70,
    SR:      int   = 5,     # Stock de Referencia (Punto de reorden)
    MAX_CAP: int   = 10,    # Capacidad máxima (S)
    ST_0:    int   = 7,
    verbose: bool  = True,
) -> dict:
    """
    Simula la política IDEAL de gestión de inventario (Revisión Continua Q,R).

    Lógica del diagrama de flujo ideal:
      · Revisión diaria continua (cada día T).
      · Si ST < SR y no hay pedido en tránsito (PE == 0):
          Se emite un pedido de tamaño TP = MAX_CAP - ST (para llegar a MAX_CAP).
      · Solo puede haber un pedido en tránsito a la vez (controlado por PE).
      · Costo total acumulado: CTF = CTALM + CVTAP + CTEP.
    """

    # ── Instanciar generadores (mismo generador congruencial compartido) ──────
    pc  = params["params_cong"]
    pr  = params["params_rechazo"]
    pu  = params["params_uniforme"]

    gen         = GeneradorCongruencial(pc["X0"], pc["a"], pc["c"], pc["m"])
    gen_demanda = GeneradorDemanda(gen, pr["lam"], pr["a_rej"], pr["b_rej"], pr["m_rej"])
    gen_demora  = GeneradorDemora(gen, pu["DE_MIN"], pu["DE_MAX"])

    # ── Estado inicial ────────────────────────────────────────────────────────
    T       = -1
    ST      = ST_0
    PE      = 0     # Bandera de pedido en camino (0=no, 1=sí)
    FLL     = 0     # Fecha de llegada del pedido
    TP      = 0     # Tamaño del pedido en camino

    CTALM   = 0.0
    CVTAP   = 0.0
    CTEP    = 0.0
    VTAP    = 0     # Unidades perdidas acumuladas
    NROP    = 0     # Número de pedidos realizados
    historial: list[dict] = []

    # ── Tabla de salida ───────────────────────────────────────────────────────
    SEP = "─" * 110
    if verbose:
        print(f"\n{'=' * 110}")
        print(f"  SIMULACIÓN — MODELO IDEAL (Revisión Continua)  |  SR={SR}  |  MAX_CAP={MAX_CAP}")
        print(f"{'=' * 110}")
        print(f"  TF={TF} días | ST₀={ST_0} | SMR=10 (Ref)")
        print(f"  CEP=${CEP} | CVP=${CVP} | CALM=${CALM}")
        print(SEP)
        print(
            f"{'T':>4} | {'VD':>3} | {'ST_ini':>6} | {'ST_fin':>6} | "
            f"{'VTAP_d':>6} | {'PE':>2} | {'Evento':<35} | "
            f"{'CTALM':>9} | {'CVTAP':>9} | {'CTEP':>7}"
        )
        print(SEP)

    # ── Loop principal ────────────────────────────────────────────────────────
    while True:
        T      += 1
        ST_ini  = ST
        llegada_hoy = False

        # [1] Recepción del pedido si T == FLL y hay pedido en tránsito
        if PE == 1 and T == FLL:
            ST += TP
            PE = 0
            FLL = 0
            llegada_hoy = True

        # [2] Generar demanda diaria
        VD = gen_demanda.siguiente()

        # [3] Atender demanda
        vtap_dia = 0
        if ST >= VD:
            ST -= VD
            CTALM += ST * CALM
        else:
            vtap_dia = VD - ST
            VTAP    += vtap_dia
            CVTAP   += vtap_dia * CVP
            ST       = 0

        # [4] Evaluar reorden (ST < SR)
        pedido_info = None
        if ST < SR:
            if PE == 0:
                TP = MAX_CAP - ST
                if TP > 0:
                    PE = 1
                    CTEP += CEP
                    NROP += 1
                    DE = gen_demora.siguiente()
                    FLL = T + DE
                    pedido_info = {"tp": TP, "de": DE, "fll": FLL}

        # Registro
        historial.append({
            "T": T, "VD": VD, "ST_ini": ST_ini, "ST": ST,
            "VTAP_dia": vtap_dia, "PE": PE, "NROP": NROP,
            "CTALM": CTALM, "CVTAP": CVTAP, "CTEP": CTEP,
            "pedido": pedido_info, "llegada": llegada_hoy
        })

        if verbose:
            evt = ""
            if llegada_hoy:
                evt += f"[llegó pedido] "
            if pedido_info:
                p    = pedido_info
                evt += f"→ Pedido: {p['tp']}u DE={p['de']} T={p['fll']}"
            print(
                f"{T:>4} | {VD:>3} | {ST_ini:>6} | {ST:>6} | "
                f"{vtap_dia:>6} | {PE:>2} | {evt:<35} | "
                f"{CTALM:>9.2f} | {CVTAP:>9.2f} | {CTEP:>7.2f}"
            )

        if T >= TF:
            break

    # ── Resultados finales ────────────────────────────────────────────────────
    CTF = CTALM + CVTAP + CTEP

    if verbose:
        print(SEP)
        print(f"  CTALM   (almacenamiento)     : $ {CTALM:>12.2f}")
        print(f"  CVTAP   (ventas perdidas)    : $ {CVTAP:>12.2f}")
        print(f"  CTEP    (emisión de pedidos) : $ {CTEP:>12.2f}")
        print(f"  {'─' * 50}")
        print(f"  CTF     (costo total ideal)  : $ {CTF:>12.2f}")
        print(f"\n  VTAP  (unidades perdidas)  :   {VTAP:>5}")
        print(f"  NROP  (pedidos realizados) :   {NROP:>5}")
        print(f"{'=' * 110}\n")

    return {
        "CTF": CTF, "CTALM": CTALM, "CVTAP": CVTAP, "CTEP": CTEP,
        "VTAP": VTAP, "NROP": NROP, "historial": historial, "gen": gen
    }
