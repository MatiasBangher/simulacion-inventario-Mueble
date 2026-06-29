import pandas as pd


def cargar_parametros(
    csv_pseudo: str = "Tablas - nro_pseudo.csv",
    csv_rechazo: str = "Tablas - M. Rechazo.csv",
    csv_inversa: str = "Tablas - Trasnformada Inversa.csv",
    csv_historico: str = "Tablas - Mueble-Camilo.csv"
) -> dict:
    """
    Lee los 4 CSVs y devuelve un dict con todos los parámetros del modelo.

    Claves del dict:
      params_cong     → X0, a, c, m
      params_rechazo  → lam, a_rej, b_rej, m_rej
      params_uniforme → DE_MIN, DE_MAX
      df_diario       → DataFrame histórico diario
      df_pedidos      → DataFrame pedidos reales
    """

    # ── Generador Congruencial Mixto ──────────────────────────────────────────
    df_ps = pd.read_csv(csv_pseudo, header=None)
    params_cong = {
        "X0": int(df_ps.iloc[0, 0]),   # semilla
        "a":  int(df_ps.iloc[1, 0]),   # multiplicador
        "c":  int(df_ps.iloc[2, 0]),   # constante aditiva
        "m":  int(df_ps.iloc[3, 0]),   # módulo
    }

    # ── Método de Rechazo (búsqueda robusta por nombre de celda) ─────────────
    df_rec_raw = pd.read_csv(csv_rechazo, header=None, nrows=7)
    pr = {"lam": 1.54, "a_rej": 0.0, "b_rej": 4.0, "m_rej": 0.35}  # defaults
    _mapeo = {"lambda": "lam", "a": "a_rej", "b": "b_rej", "m": "m_rej"}
    for _, fila in df_rec_raw.iterrows():
        vals = fila.dropna().astype(str).tolist()
        for i, v in enumerate(vals):
            clave = _mapeo.get(v.strip().lower())
            if clave and i + 1 < len(vals):
                try:
                    pr[clave] = float(vals[i + 1])
                except ValueError:
                    pass
    params_rechazo = pr

    # ── Transformada Inversa — extrae DE_MIN y DE_MAX del CSV ─────────────────
    df_inv = pd.read_csv(csv_inversa, header=4, usecols=[1, 2, 3, 4])
    df_inv.columns = ["nro", "r", "Fr", "redondeo"]
    df_inv["nro"]      = pd.to_numeric(df_inv["nro"],      errors="coerce")
    df_inv["redondeo"] = pd.to_numeric(df_inv["redondeo"], errors="coerce")
    df_inv = df_inv.dropna(subset=["nro", "redondeo"])
    df_inv = df_inv[df_inv["nro"].between(1, 50)]
    params_uniforme = {
        "DE_MIN": int(df_inv["redondeo"].min()),
        "DE_MAX": int(df_inv["redondeo"].max()),
    }

    # ── Datos históricos observados ───────────────────────────────────────────
    df_hist = pd.read_csv(csv_historico, header=2)
    num_cols = len(df_hist.columns)
    
    col_names = [
        "idx", "semana", "fecha", "stock_ini", "demanda_total",
        "unidades_vendidas", "dem_insatisfecha", "pedido_prov", "stock_fin"
    ]
    
    if num_cols >= 15:
        # Si tiene las columnas adicionales a la derecha (pedidos)
        df_hist.columns = col_names + ["sep", "nro_pedido", "dia_pedido", "dia_llegada", "demora_cal", "demora_hab"]
        df_pedidos = (
            df_hist[df_hist["nro_pedido"].notna()]
            .copy()[["nro_pedido", "dia_pedido", "dia_llegada", "demora_cal", "demora_hab"]]
            .dropna(subset=["nro_pedido"])
        )
        df_pedidos["demora_hab"] = pd.to_numeric(df_pedidos["demora_hab"], errors="coerce")
    else:
        # Si solo tiene las columnas básicas de diario
        df_hist.columns = col_names[:num_cols]
        df_pedidos = pd.DataFrame(columns=["nro_pedido", "dia_pedido", "dia_llegada", "demora_hab"])
        
    mask_fecha  = df_hist["fecha"].notna() & df_hist["fecha"].astype(str).str.contains("/")
    df_diario   = df_hist[mask_fecha].copy()[[
        "fecha", "semana", "stock_ini", "unidades_vendidas",
        "dem_insatisfecha", "pedido_prov", "stock_fin"
    ]].reset_index(drop=True)
    for col in ["stock_ini", "unidades_vendidas", "stock_fin"]:
        df_diario[col] = pd.to_numeric(df_diario[col], errors="coerce")
    df_diario["dem_insatisfecha"] = (
        pd.to_numeric(df_diario["dem_insatisfecha"], errors="coerce").fillna(0).astype(int)
    )


    return {
        "params_cong":     params_cong,
        "params_rechazo":  params_rechazo,
        "params_uniforme": params_uniforme,
        "df_diario":       df_diario,
        "df_pedidos":      df_pedidos,
    }


def imprimir_parametros(params: dict):
    pc = params["params_cong"]

    print(f"\n{'=' * 70}")
    print("  📁  PARÁMETROS LEÍDOS DESDE LOS CSVs")
    print(f"{'=' * 70}")
    print(f"\n  Generador Congruencial Mixto:")
    print(f"    Xₙ₊₁ = ({pc['a']}·Xₙ + {pc['c']}) mod {pc['m']}   X₀ = {pc['X0']}")
    print(f"{'=' * 70}")
