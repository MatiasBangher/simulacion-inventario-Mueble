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
# Gráfico 1 — Histograma del CTF
# ─────────────────────────────────────────────────────────────────────────────
def _plot_histograma(ax, costos: list, alfa: float):
    mean, margin, ci_lo, ci_hi = _intervalo_confianza(costos, alfa)

    ax.hist(costos, bins=45, color=C_HIST, alpha=0.80,
            edgecolor=BG_GLOBAL, linewidth=0.4)

    ax.axvline(mean, color=C_MEDIA, linewidth=2.0, linestyle="--",
               label=f"Media: ${mean:,.0f}")
    ax.axvline(ci_lo, color=C_IC, linewidth=1.5, linestyle=":",
               label=f"IC {int((1-alfa)*100)}%:  [${ci_lo:,.0f} — ${ci_hi:,.0f}]")
    ax.axvline(ci_hi, color=C_IC, linewidth=1.5, linestyle=":")
    ax.axvspan(ci_lo, ci_hi, alpha=0.10, color=C_IC)

    _formato_ax(ax)
    ax.set_title("Distribución del CTF  (1.500 réplicas)",
                 color=C_TEXT, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Costo Total de Funcionamiento  ($)")
    ax.set_ylabel("Frecuencia")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(_fmt_millones))
    ax.legend(fontsize=8, facecolor="#21262d", edgecolor=C_BORDER,
              labelcolor=C_TEXT, framealpha=0.9)


# ─────────────────────────────────────────────────────────────────────────────
# Gráfico 2 — Torta de composición del CTF
# ─────────────────────────────────────────────────────────────────────────────
def _plot_torta(ax, avg_vtap, avg_ctep, avg_alm, avg_sob):
    labels  = ["Ventas Perdidas\n(CVTAP)",
               "Emisión Pedidos\n(CTEP)",
               "Almac. Regular\n(CTALM)",
               "Almac. Sobrante\n(CALMSOB)"]
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
# Gráfico 3 — Convergencia de la media del CTF
# ─────────────────────────────────────────────────────────────────────────────
def _plot_convergencia(ax, costos: list, alfa: float):
    n = len(costos)
    # Media acumulada
    acum, running = 0.0, []
    for i, v in enumerate(costos):
        acum += v
        running.append(acum / (i + 1))

    mean, _, ci_lo, ci_hi = _intervalo_confianza(costos, alfa)
    reps = list(range(1, n + 1))

    ax.plot(reps, running, color=C_CONV, linewidth=1.4, alpha=0.9)
    ax.axhline(mean, color=C_MEDIA, linewidth=1.8, linestyle="--",
               label=f"Valor estabilizado: ${mean:,.0f}")
    ax.fill_between(reps, ci_lo, ci_hi, alpha=0.12, color=C_IC,
                    label=f"IC {int((1-alfa)*100)}%: ± ${(ci_hi - ci_lo)/2:,.0f}")

    _formato_ax(ax)
    ax.set_title("Convergencia de la Media del CTF",
                 color=C_TEXT, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Número de réplicas")
    ax.set_ylabel("Media acumulada  ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_fmt_millones))
    ax.legend(fontsize=8.5, facecolor="#21262d", edgecolor=C_BORDER,
              labelcolor=C_TEXT, framealpha=0.9)


# ─────────────────────────────────────────────────────────────────────────────
# Gráfico 4 — Barras por componente con barra de error (± 1σ)
# ─────────────────────────────────────────────────────────────────────────────
def _plot_barras_componentes(ax, alm, sob, vtap_cost, emision):
    etiquetas = ["CVTAP\n(Ventas\nPerdidas)",
                 "CTEP\n(Emisión\nPedidos)",
                 "CTALM\n(Almac.\nRegular)",
                 "CALMSOB\n(Almac.\nSobrante)"]
    colores = [C_CVTAP, C_CTEP, C_CTALM, C_CALMSOB]
    series  = [vtap_cost, emision, alm, sob]

    medias = [sum(s) / len(s) for s in series]
    desv   = [_std(s, m) for s, m in zip(series, medias)]

    bars = ax.bar(etiquetas, medias, color=colores, alpha=0.85,
                  edgecolor=BG_GLOBAL, linewidth=1.2, width=0.55)
    ax.errorbar(etiquetas, medias, yerr=desv, fmt="none",
                color=C_TEXT, capsize=6, linewidth=1.5, capthick=1.5)

    # Etiquetas de valor sobre cada barra
    for bar, m, s in zip(bars, medias, desv):
        ax.text(bar.get_x() + bar.get_width() / 2.0,
                m + s + max(medias) * 0.02,
                f"${m/1_000:.0f}k",
                ha="center", va="bottom",
                color=C_TEXT, fontsize=9, fontweight="bold")

    _formato_ax(ax)
    ax.set_title("Costo Promedio por Componente  (± 1σ)",
                 color=C_TEXT, fontsize=12, fontweight="bold", pad=10)
    ax.set_ylabel("Costo Promedio  ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_fmt_millones))


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
    TF:               int  = 70,
    alfa:             float = 0.05,
    guardar:          bool  = True,
    nombre_archivo:   str   = "graficas_situacion_actual.png",
):
    """
    Genera un panel de 4 gráficas para el análisis de la Situación Actual:
      1. Histograma del CTF con media e IC al 95%
      2. Torta de composición de costos
      3. Convergencia de la media del CTF
      4. Barras por componente con desvío estándar

    Parámetros
    ----------
    costos_actual    : lista de CTF por réplica
    alm_actual       : lista de CTALM por réplica
    sob_actual       : lista de CALMSOB por réplica
    vtap_cost_actual : lista de CVTAP por réplica
    emision_actual   : lista de CTEP por réplica
    N_REPLICACIONES  : cantidad total de réplicas
    TF               : tiempo final de simulación (días corridos)
    alfa             : nivel de significancia (default 0.05 → IC 95%)
    guardar          : si True, guarda la imagen en disco
    nombre_archivo   : nombre del archivo PNG de salida
    """
    # Promedios para la torta
    avg_vtap   = sum(vtap_cost_actual) / N_REPLICACIONES
    avg_ctep   = sum(emision_actual)   / N_REPLICACIONES
    avg_alm    = sum(alm_actual)       / N_REPLICACIONES
    avg_sob    = sum(sob_actual)       / N_REPLICACIONES

    _, _, ci_lo, ci_hi = _intervalo_confianza(costos_actual, alfa)

    # ── Layout ────────────────────────────────────────────────────────────────
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(18, 11), facecolor=BG_GLOBAL)
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.32)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    _plot_histograma(ax1, costos_actual, alfa)
    _plot_torta(ax2, avg_vtap, avg_ctep, avg_alm, avg_sob)
    _plot_convergencia(ax3, costos_actual, alfa)
    _plot_barras_componentes(ax4, alm_actual, sob_actual, vtap_cost_actual, emision_actual)

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
    return fig
