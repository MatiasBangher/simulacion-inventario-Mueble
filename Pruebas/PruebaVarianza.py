from scipy import stats


def prueba_varianza_con_chi2(numeros: list, nivel_confianza: float) -> bool:
    """
    Prueba de Varianza.
    H₀: σ² = 1/12 ≈ 0.083333  (distribución Uniforme(0,1))
    Estadístico: χ² = 12 · (n - 1) · S²
    Acepta H₀ si χ²_lim_inf ≤ χ² ≤ χ²_lim_sup
    """
    n = len(numeros)
    if n < 2:
        return False
    media = sum(numeros) / n
    S2 = sum((x - media) ** 2 for x in numeros) / (n - 1)
    chi2 = 12 * (n - 1) * S2
    alfa = 1 - nivel_confianza
    gl = n - 1
    li = stats.chi2.ppf(alfa / 2, df=gl)
    ls = stats.chi2.ppf(1 - alfa / 2, df=gl)
    return bool(li <= chi2 <= ls)

