import math
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats


# ─────────────────────────────────────────────────────────────────────────────
# Paleta visual (tema oscuro premium)
# ─────────────────────────────────────────────────────────────────────────────
BG_GLOBAL  = "#0d1117"
BG_PANEL   = "#161b22"
C_TEXT     = "#e6edf3"
C_SUBTEXT  = "#8b949e"
C_BORDER   = "#30363d"

# Colores por componente de costo (consistentes en todos los gráficos)
C_CVTAP   = "#f06292"   # rojo-rosa  → ventas perdidas (el más grave)
C_CTEP    = "#ffa726"   # naranja    → emisión de pedidos
C_CTALM   = "#4fc3f7"   # celeste    → almacenamiento regular
C_CALMSOB = "#ab47bc"   # violeta    → almacenamiento sobrante

C_MEDIA   = "#f06292"   # línea de media
C_IC      = "#66bb6a"   # banda / líneas de IC
C_HIST    = "#4fc3f7"   # barras del histograma
C_CONV    = "#4fc3f7"   # línea de convergencia


def _std(data: list, mean: float) -> float:
    """Desvío estándar muestral."""
    n = len(data)
    return math.sqrt(sum((x - mean) ** 2 for x in data) / (n - 1))


def _intervalo_confianza(data: list, alfa: float = 0.05) -> tuple:
    """Devuelve (media, margen, ci_lower, ci_upper) con t de Student."""
    n    = len(data)
    mean = sum(data) / n
    s    = _std(data, mean)
    t    = stats.t.ppf(1 - alfa / 2, df=n - 1)
    margin = t * s / math.sqrt(n)
    return mean, margin, mean - margin, mean + margin


def _formato_ax(ax):
    """Aplica estilo oscuro estándar a un eje."""
    ax.set_facecolor(BG_PANEL)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["bottom", "left"]:
        ax.spines[spine].set_color(C_BORDER)
    ax.tick_params(colors=C_SUBTEXT, labelsize=9)
    ax.xaxis.label.set_color(C_SUBTEXT)
    ax.yaxis.label.set_color(C_SUBTEXT)


def _fmt_millones(x, _):
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.1f}M"
    return f"${x/1_000:.0f}k"

# ─────────────────────────────────────────────────────────────────────────────
# Gráfico 1 — Histograma del CTF con media e IC
# ─────────────────────────────────────────────────────────────────────────────
def _plot_histograma(ax, costos: list, alfa: float):
    """Histograma del CTF con media e intervalo de confianza."""
    mean, _, ci_lo, ci_hi = _intervalo_confianza(costos, alfa)
    n_bins = max(20, int(len(costos) ** 0.5))

    ax.hist(costos, bins=n_bins, color=C_HIST, alpha=0.80, edgecolor=BG_GLOBAL, linewidth=0.4)
    ax.axvline(mean,  color=C_MEDIA, linewidth=2.0, linestyle="--",
               label=f"Media: ${mean:,.0f}")
    ax.axvline(ci_lo, color=C_IC,    linewidth=1.4, linestyle=":")
    ax.axvline(ci_hi, color=C_IC,    linewidth=1.4, linestyle=":",
               label=f"IC {int((1-alfa)*100)}%: \u00b1 ${(ci_hi - ci_lo)/2:,.0f}")
    ax.fill_betweenx([0, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 1],
                     ci_lo, ci_hi, alpha=0.08, color=C_IC)

    _formato_ax(ax)
    ax.set_title("Distribución del CTF",
                 color=C_TEXT, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Costo Total de Funcionamiento ($)")
    ax.set_ylabel("Frecuencia (réplicas)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(_fmt_millones))
    ax.legend(fontsize=8.5, facecolor="#21262d", edgecolor=C_BORDER,
              labelcolor=C_TEXT, framealpha=0.9)


# ─────────────────────────────────────────────────────────────────────────────
# Gráfico 2 — Torta de composición del CTF
# ─────────────────────────────────────────────────────────────────────────────
def _plot_torta(ax, avg_vtap, avg_ctep, avg_alm, avg_sob):
    labels  = ["Costo de Ventas Perdidas\n(CVTAP)",
               "Costo de Emisión de Pedidos\n(CTEP)",
               "Costo de Almacenamiento Regular\n(CTALM)",
               "Costo de Almacenamiento Sobrante\n(CALMSOB)"]
    sizes   = [avg_vtap, avg_ctep, avg_alm, avg_sob]
    colors  = [C_CVTAP, C_CTEP, C_CTALM, C_CALMSOB]
    explode = (0.06, 0, 0, 0)

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        explode=explode,
        autopct="%1.1f%%",
        startangle=150,
        textprops={"color": C_TEXT, "fontsize": 8.5},
        wedgeprops={"linewidth": 2, "edgecolor": BG_GLOBAL},
        pctdistance=0.72,
    )
    for at in autotexts:
        at.set_color(BG_GLOBAL)
        at.set_fontweight("bold")
        at.set_fontsize(9)

    ax.set_facecolor(BG_PANEL)
    ax.set_title("Composición del CTF Promedio",
                 color=C_TEXT, fontsize=12, fontweight="bold", pad=10)


# ─────────────────────────────────────────────────────────────────────────────
# Gráfico 3 — Convergencia de la media (genérico)
# ─────────────────────────────────────────────────────────────────────────────
def _plot_convergencia(
    ax, costos: list, alfa: float,
    titulo: str = "Convergencia de la Media del CTF",
    color_linea: str = C_CONV,
):
    """Dibuja la convergencia de la media acumulada de *costos* en el eje *ax*."""
    n = len(costos)
    # Media acumulada
    acum, running = 0.0, []
    for i, v in enumerate(costos):
        acum += v
        running.append(acum / (i + 1))

    mean, _, ci_lo, ci_hi = _intervalo_confianza(costos, alfa)
    reps = list(range(1, n + 1))

    ax.plot(reps, running, color=color_linea, linewidth=1.4, alpha=0.9)
    ax.axhline(mean, color=C_MEDIA, linewidth=1.8, linestyle="--",
               label=f"Estabilizado: ${mean:,.0f}")
    ax.fill_between(reps, ci_lo, ci_hi, alpha=0.12, color=C_IC,
                    label=f"IC {int((1-alfa)*100)}%: ± ${(ci_hi - ci_lo)/2:,.0f}")

    _formato_ax(ax)
    ax.set_title(titulo, color=C_TEXT, fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel("Número de réplicas")
    ax.set_ylabel("Media acumulada  ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_fmt_millones))
    ax.legend(fontsize=8, facecolor="#21262d", edgecolor=C_BORDER,
              labelcolor=C_TEXT, framealpha=0.9)


# ─────────────────────────────────────────────────────────────────────────────
# Gráfico 4 — Barras por componente de costo
# ─────────────────────────────────────────────────────────────────────────────
def _plot_barras(ax, avg_vtap, avg_ctep, avg_alm, avg_sob,
                 vtap_list, ctep_list, alm_list, sob_list):
    """Barras horizontales por componente con desviación estándar."""
    labels = ["CVTAP\n(Ventas Perd.)", "CTEP\n(Emisión Ped.)",
              "CTALM\n(Almac. Reg.)",  "CALMSOB\n(Almac. Sob.)"]
    medias = [avg_vtap, avg_ctep, avg_alm, avg_sob]
    errs   = [_std(lst, m) for lst, m in
              zip([vtap_list, ctep_list, alm_list, sob_list], medias)]
    colors = [C_CVTAP, C_CTEP, C_CTALM, C_CALMSOB]
    y_pos  = list(range(len(labels)))

    bars = ax.barh(y_pos, medias, xerr=errs, color=colors,
                   align="center", alpha=0.85, height=0.55,
                   error_kw={"ecolor": C_TEXT, "capsize": 4,
                              "linewidth": 1.2, "alpha": 0.7},
                   edgecolor=BG_GLOBAL, linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color=C_TEXT, fontsize=8.5)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(_fmt_millones))

    for bar, val in zip(bars, medias):
        ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                f"${val:,.0f}", va="center", ha="left",
                color=C_TEXT, fontsize=7.5)

    _formato_ax(ax)
    ax.set_title("Costo Promedio por Componente (± 1σ)",
                 color=C_TEXT, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Costo promedio ($)")


# ─────────────────────────────────────────────────────────────────────────────
# Figura extra — Convergencia de todos los costos
# ─────────────────────────────────────────────────────────────────────────────
def _plot_convergencias_costos(
    ctf:    list,
    cvtap:  list,
    ctep:   list,
    ctalm:  list,
    calmsob: list,
    alfa:   float,
    N_REPLICACIONES: int,
    TF:     int,
    guardar: bool  = True,
    nombre_archivo: str = "graficas_convergencia_costos.png",
):
    """Genera una figura con 5 diagramas de convergencia: CTF y los 4 componentes."""
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(20, 12), facecolor=BG_GLOBAL)
    gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.50, wspace=0.35)

    # Fila superior: CTF (destacado, ancho doble) + CVTAP
    ax_ctf    = fig.add_subplot(gs[0, 0:2])  # span 2 columnas
    ax_cvtap  = fig.add_subplot(gs[0, 2])
    # Fila inferior: CTEP, CTALM, CALMSOB
    ax_ctep   = fig.add_subplot(gs[1, 0])
    ax_ctalm  = fig.add_subplot(gs[1, 1])
    ax_csob   = fig.add_subplot(gs[1, 2])

    series = [
        (ax_ctf,   ctf,     "Convergencia — CTF (Costo Total de Funcionamiento)",  "#64b5f6"),
        (ax_cvtap, cvtap,   "Convergencia — CVTAP (Ventas Perdidas)",               C_CVTAP),
        (ax_ctep,  ctep,    "Convergencia — CTEP (Emisión de Pedidos)",              C_CTEP),
        (ax_ctalm, ctalm,   "Convergencia — CTALM (Almacenamiento Regular)",         C_CTALM),
        (ax_csob,  calmsob, "Convergencia — CALMSOB (Almacenamiento Sobrante)",      C_CALMSOB),
    ]
    for ax, data, titulo, color in series:
        _plot_convergencia(ax, data, alfa, titulo=titulo, color_linea=color)

    _, _, ci_lo, ci_hi = _intervalo_confianza(ctf, alfa)
    fig.suptitle(
        f"Convergencia de Costos — Situación Actual  |  Mueble Camilo (S&M)\n"
        f"N = {N_REPLICACIONES:,} réplicas  ·  TF = {TF} días corridos  ·  "
        f"IC {int((1-alfa)*100)}% CTF: [ ${ci_lo:,.0f}  —  ${ci_hi:,.0f} ]",
        color=C_TEXT, fontsize=13, fontweight="bold", y=0.998,
    )

    if guardar:
        plt.savefig(nombre_archivo, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"  📈  Convergencia guardada en → {nombre_archivo}")

    plt.show()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Función pública principal
# ─────────────────────────────────────────────────────────────────────────────
def generar_graficas_actual(
    costos_actual:    list,
    alm_actual:       list,
    sob_actual:       list,
    vtap_cost_actual: list,
    emision_actual:   list,
    N_REPLICACIONES:  int,
    TF:               int   = 70,
    alfa:             float = 0.05,
    guardar:          bool  = True,
    nombre_archivo:         str = "graficas_situacion_actual.png",
    nombre_archivo_conv:    str = "graficas_convergencia_costos.png",
):
    """
    Genera dos figuras para el análisis de la Situación Actual:

    Figura 1 — Panel general (4 subplots):
      1. Histograma del CTF con media e IC al 95%
      2. Torta de composición de costos
      3. Convergencia de la media del CTF
      4. Barras por componente con desvío estándar

    Figura 2 — Convergencia de todos los costos (5 subplots):
      CTF, CVTAP, CTEP, CTALM, CALMSOB

    Parámetros
    ----------
    costos_actual       : lista de CTF por réplica
    alm_actual          : lista de CTALM por réplica
    sob_actual          : lista de CALMSOB por réplica
    vtap_cost_actual    : lista de CVTAP por réplica
    emision_actual      : lista de CTEP por réplica
    N_REPLICACIONES     : cantidad total de réplicas
    TF                  : tiempo final de simulación (días corridos)
    alfa                : nivel de significancia (default 0.05 → IC 95%)
    guardar             : si True, guarda las imágenes en disco
    nombre_archivo      : nombre del PNG del panel general
    nombre_archivo_conv : nombre del PNG de convergencia de costos
    """
    # Promedios para la torta
    avg_vtap   = sum(vtap_cost_actual) / N_REPLICACIONES
    avg_ctep   = sum(emision_actual)   / N_REPLICACIONES
    avg_alm    = sum(alm_actual)       / N_REPLICACIONES
    avg_sob    = sum(sob_actual)       / N_REPLICACIONES

    _, _, ci_lo, ci_hi = _intervalo_confianza(costos_actual, alfa)

    # ── Figura 1: Torta + Convergencia CTF (layout 1×2) ──────────────────────
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(16, 7), facecolor=BG_GLOBAL)
    gs  = gridspec.GridSpec(1, 2, figure=fig, wspace=0.38)

    ax_torta = fig.add_subplot(gs[0, 0])
    ax_conv  = fig.add_subplot(gs[0, 1])

    _plot_torta(ax_torta, avg_vtap, avg_ctep, avg_alm, avg_sob)
    _plot_convergencia(
        ax_conv, costos_actual, alfa,
        titulo="Convergencia de la Media del CTF",
        color_linea=C_CONV,
    )

    # ── Título global ─────────────────────────────────────────────────────────
    fig.suptitle(
        f"Simulación Monte Carlo — Situación Actual  |  Mueble Camilo (S&M)\n"
        f"N = {N_REPLICACIONES:,} réplicas  ·  TF = {TF} días corridos  ·  "
        f"IC {int((1-alfa)*100)}%: [ ${ci_lo:,.0f}  —  ${ci_hi:,.0f} ]",
        color=C_TEXT, fontsize=13, fontweight="bold", y=0.995,
    )

    if guardar:
        plt.savefig(nombre_archivo, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"\n  📊  Gráficas guardadas en → {nombre_archivo}")

    plt.show()

    # ── Figura 2: Convergencia de todos los costos ────────────────────────────
    fig2 = _plot_convergencias_costos(
        ctf      = costos_actual,
        cvtap    = vtap_cost_actual,
        ctep     = emision_actual,
        ctalm    = alm_actual,
        calmsob  = sob_actual,
        alfa     = alfa,
        N_REPLICACIONES = N_REPLICACIONES,
        TF       = TF,
        guardar  = guardar,
        nombre_archivo = nombre_archivo_conv,
    )

    return fig, fig2
