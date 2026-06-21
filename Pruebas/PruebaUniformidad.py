import math
from scipy import stats


def prueba_uniformidad_con_chi2(numeros: list, nivel_confianza: float, k: int = None) -> bool:
    """
    Prueba de Uniformidad (Chi-Cuadrada).
    H₀: los números siguen una distribución Uniforme(0,1)
    Se divide en k intervalos.
    Acepta H₀ si χ² ≤ χ²_crítico
    """
    n = len(numeros)
    if k is None:
        k = max(5, round(math.sqrt(n)))

    E = n / k  # Frecuencia esperada
    frecuencias = [0] * k
    for r in numeros:
        idx = min(int(r * k), k - 1)
        frecuencias[idx] += 1

    chi2 = sum((O - E) ** 2 / E for O in frecuencias)
    alfa = 1 - nivel_confianza
    gl = k - 1
    critico = stats.chi2.ppf(1 - alfa, df=gl)
    return bool(chi2 <= critico)

