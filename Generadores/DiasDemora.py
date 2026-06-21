from Pruebas.GenNumsAleatorios import GeneradorCongruencial


class GeneradorDemora:
    """
    Genera demora del proveedor por Transformada Inversa.
    DE ~ Uniforme(DE_MIN, DE_MAX)  →  F⁻¹(r) = DE_MIN + (DE_MAX − DE_MIN)·r
    """

    def __init__(self, gen: GeneradorCongruencial, de_min: int, de_max: int):
        self.gen = gen
        self.de_min = de_min
        self.de_max = de_max

    def siguiente(self) -> int:
        r = self.gen.siguiente()
        return round(self.de_min + (self.de_max - self.de_min) * r)
