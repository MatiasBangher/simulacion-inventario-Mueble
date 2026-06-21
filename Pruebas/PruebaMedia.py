import math
from scipy import stats


def prueba_media_con_z(numeros: list, nivel_confianza: float) -> bool:
    """
    Prueba de Media.
    H₀: μ = 0.5  (distribución Uniforme(0,1))
    Estadístico: Z = (r̄ - 0.5) · √(12·n)
    Acepta H₀ si |Z| ≤ z_{α/2}
    """
    n = len(numeros)
    media = sum(numeros) / n
    Z = (media - 0.5) * math.sqrt(12 * n)
    alfa = 1 - nivel_confianza
    z_critico = stats.norm.ppf(1 - alfa / 2)
    return bool(abs(Z) <= z_critico)

