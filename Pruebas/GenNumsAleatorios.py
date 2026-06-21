class GeneradorCongruencial:
    """
    Genera números pseudoaleatorios rₙ ∈ [0, 1) dinámicamente
    usando el Método Congruencial Mixto.
    """

    def __init__(self, X0: int, a: int, c: int, m: int):
        self.a = a
        self.c = c
        self.m = m
        self.Xn = X0
        self.count = 0
        self._historial = []

    def siguiente(self) -> float:
        """Devuelve el próximo r pseudoaleatorio."""
        self.Xn = (self.a * self.Xn + self.c) % self.m
        r = self.Xn / self.m
        self.count += 1
        self._historial.append(r)
        return r

    def generar_n(self, n: int) -> list[float]:
        """Genera y retorna una lista de n valores."""
        return [self.siguiente() for _ in range(n)]

    @property
    def secuencia(self) -> list[float]:
        """Retorna todos los r generados hasta ahora."""
        return list(self._historial)
