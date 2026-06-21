import math
from Pruebas.GenNumsAleatorios import GeneradorCongruencial


def poisson_pmf(x: int, lam: float) -> float:
    """P(X = x) para Poisson(λ)."""
    if x < 0:
        return 0.0
    return (lam ** x) * math.exp(-lam) / math.factorial(x)


class GeneradorDemanda:
    """
    Genera demanda diaria por Método de Rechazo (Poisson(λ)).
    Usa el mismo GeneradorCongruencial compartido de la corrida.
    """

    def __init__(self, gen: GeneradorCongruencial,
                 lam: float, a: float, b: float, M: float):
        self.gen = gen
        self.lam = lam
        self.a = a
        self.b = b
        self.M = M
        self.intentos = 0
        self.aceptados = 0

    def siguiente(self) -> int:
        while True:
            r1 = self.gen.siguiente()
            r2 = self.gen.siguiente()
            self.intentos += 1

            x = self.a + (self.b - self.a) * r1
            xi = round(x)
            fx = poisson_pmf(xi, self.lam)

            if r2 <= fx / self.M:
                self.aceptados += 1
                return xi
