import math
from scipy import stats


def prueba_corrida_arriba_abajo(numeros: list, nivel_confianza: float) -> bool:
    """
    Prueba de Independencia - Corrida Arriba y Abajo.
    Acepta H₀ si |Z| ≤ z_{α/2}
    """
    n = len(numeros)
    if n < 3:
        return False

    signos = []
    for i in range(1, n):
        if numeros[i] > numeros[i - 1]:
            signos.append(1)
        elif numeros[i] < numeros[i - 1]:
            signos.append(-1)

    if not signos:
        return False

    A = 1
    for i in range(1, len(signos)):
        if signos[i] != signos[i - 1]:
            A += 1

    mu_A = (2 * n - 1) / 3
    var_A = (16 * n - 29) / 90
    
    if var_A <= 0:
        return False
        
    Z = (A - mu_A) / math.sqrt(var_A)
    alfa = 1 - nivel_confianza
    z_critico = stats.norm.ppf(1 - alfa / 2)
    return bool(abs(Z) <= z_critico)



def prueba_corrida_arriba_abajo_media(numeros: list, nivel_confianza: float) -> bool:
    """
    Prueba de Independencia - Corrida Arriba y Abajo de la Media.
    Acepta H₀ si |Z| ≤ z_{α/2}
    """
    n = len(numeros)
    if n < 3:
        return False

    codigos = [1 if r >= 0.5 else 0 for r in numeros]
    n1 = sum(codigos)
    n2 = n - n1

    if n1 == 0 or n2 == 0:
        return False

    G = 1
    for i in range(1, len(codigos)):
        if codigos[i] != codigos[i - 1]:
            G += 1

    EG = (2 * n1 * n2) / n + 1
    denom = (n ** 2) * (n - 1)
    if denom <= 0:
        return False
        
    VG = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / denom
    
    if VG <= 0:
        return False

    Z = (G - EG) / math.sqrt(VG)
    alfa = 1 - nivel_confianza
    z_critico = stats.norm.ppf(1 - alfa / 2)
    return bool(abs(Z) <= z_critico)

