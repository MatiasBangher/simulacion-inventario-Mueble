# Simulación de Gestión de Almacenamiento — Mueble "Camilo" (S&M)

Este repositorio contiene la simulación de Monte Carlo del comportamiento de almacenamiento y gestión de stock del mueble **"Camilo"** (alacena + bajo mesada de 1.40m en MDF blanco) para la empresa **Servicios y Materiales (S&M)** ubicada en Resistencia, Chaco.

El proyecto está modularizado, estructurado con buenas prácticas de programación en Python y validado mediante pruebas estadísticas de aleatoriedad e independencia.

---

## 🎯 Objetivo de la Simulación

Analizar el comportamiento actual de la gestión de almacenamiento del mueble "Camilo", evaluando su impacto en los costos asociados al inventario (almacenamiento regular, ventas perdidas, emisión de pedidos y almacenamiento de stock sobrante) con el fin de identificar oportunidades de mejora en la administración de stock.

---

## 📁 Estructura del Proyecto

El código está organizado en paquetes y módulos independientes para facilitar su mantenimiento y escalabilidad:

```text
simulacion-inventario-Mueble/
├── Generadores/                  # Generación de variables aleatorias
│   ├── __init__.py
│   ├── Demanda.py                # Demanda diaria (Método de Rechazo - Poisson)
│   └── DiasDemora.py             # Demora del proveedor (Transformada Inversa)
│
├── Pruebas/                      # Pruebas estadísticas y números aleatorios
│   ├── __init__.py
│   ├── GenNumsAleatorios.py       # Generador Congruencial Mixto
│   ├── PruebaMedia.py             # Prueba de Media (Z-Test)
│   ├── PruebaVarianza.py          # Prueba de Varianza (Chi-Cuadrado)
│   ├── PruebaUniformidad.py       # Prueba de Uniformidad (Chi-Cuadrado)
│   ├── PruebasIndependencia.py    # Pruebas de Corridas (Arriba/Abajo y de la Media)
│   └── DistUniformeSim.py         # Suite integrada de ejecución de pruebas
│
├── Tablas - M. Rechazo.csv       # Datos históricos y parámetros de demanda (Poisson)
├── Tablas - Trasnformada Inversa.csv # Datos de demora del proveedor
├── Tablas - nro_pseudo.csv       # Semillas y parámetros del generador congruencial
├── Tablas - Mueble-Camilo.csv    # Datos históricos reales registrados
│
├── datos.py                      # Módulo de carga de parámetros y CSVs (Pandas)
├── simulacion_actual.py          # Lógica de simulación de la situación actual (a ojo)
├── simulacion_ideal.py           # Lógica de simulación del modelo ideal (revisión continua)
├── main.py                       # Punto de entrada, optimización de SR y comparativa
├── test_suite.py                 # Suite de pruebas unitarias
└── README.md                     # Documentación general del proyecto

```

---

## 🛠️ Metodología Utilizada

### 1. Generación de Números Pseudoaleatorios
Se utiliza el **Método Congruencial Mixto** parametrizado a través de los valores del archivo `Tablas - nro_pseudo.csv`:
$$X_{n+1} = (a \cdot X_n + c) \pmod{m}$$
$$r_n = \frac{X_n}{m}$$

### 2. Generación de Variables Aleatorias
* **Demanda Diaria**: Se modela usando una distribución de **Poisson ($\lambda = 1.54$)** implementada mediante el **Método de Rechazo** utilizando pares de números aleatorios uniformes.
* **Demora del Proveedor (DE)**: Se modela usando una distribución **Uniforme discreta** implementada mediante la **Transformada Inversa**.

### 3. Pruebas Estadísticas Realizadas
Para garantizar que la secuencia de números pseudoaleatorios generados es válida para simular, el sistema ejecuta automáticamente 5 pruebas sobre el total de números generados durante la corrida:
1. **Prueba de Media** (Z)
2. **Prueba de Varianza** ($\chi^2$)
3. **Prueba de Uniformidad** (Bondad de Ajuste $\chi^2$)
4. **Prueba de Independencia — Corrida Arriba y Abajo** (Z)
5. **Prueba de Independencia — Corrida Arriba y Abajo de la Media** (Z)

---

## 🚀 Instrucciones de Ejecución

### Requisitos Previos
Asegúrate de tener instaladas las librerías necesarias ejecutando:
```bash
pip install pandas scipy
```

### Ejecutar la Simulación
Para correr el modelo de la situación actual y desplegar los resultados financieros detallados del almacenamiento junto a los resultados de las pruebas estadísticas, ejecuta:
```bash
python main.py
```

### Ejecutar la Suite de Pruebas Unitarias
Para correr los tests automatizados que validan los generadores individuales y las pruebas estadísticas:
```bash
python test_suite.py
```

---

## 📊 Configuración de Variables en `main.py`

En la parte superior de `main.py` puedes modificar los siguientes parámetros para alterar el escenario o costos del modelo:

```python
# Costos (en $)
CEP     = 100.0    # Costo de emisión por pedido ($/pedido)
CVP     = 250.0    # Costo de venta perdida ($/unidad)
CALM    = 2.0      # Costo de almacenamiento regular ($/unidad·día)
CSOB    = 5.0      # Costo de almacenamiento sobrante ($/unidad·día) (Solo Modelo Actual)

# Simulación
TF      = 70       # Tiempo final de simulación (días corridos)
SMR     = 10       # Stock Medio de Referencia (punto de reorden)
MAX_CAP = 10       # Capacidad máxima del depósito
ST_0    = 7        # Stock inicial
```

---

## 📈 Comparativa de Modelos: Actual vs. Ideal

Al ejecutar la simulación, `main.py` corre de forma secuencial:
1. **Situación Actual**: Bucle semanal (revisión los lunes) con un pedido "a ojo" entre $1$ y $(SMR - ST)$.
2. **Modelo Ideal**: Bucle diario (revisión continua) con reorden cuando $ST < SR$. Si se cumple la condición y no hay pedidos pendientes (`PE == 0`), se ordena una cantidad exacta de $TP = MAX\_CAP - ST$.

### 🔄 Réplicas Monte Carlo
Para obtener estimaciones estadísticamente estables e independientes de las condiciones iniciales de una única corrida, `main.py` ejecuta **1.500 réplicas** de cada modelo (situación actual y cada escenario de $SR$ del modelo ideal), promediando los costos e indicadores de salida.

### 📅 Datos de Demora: Transformada Inversa "de corrido"
A sugerencia de la cátedra, la simulación utiliza el archivo `Tablas - Trasnformada Inversa de corrido.csv`. Este modelo de demora calcula los tiempos de entrega del proveedor basándose en días corridos totales (**sin diferenciar entre días hábiles y no hábiles**), lo cual se ve reflejado en los tiempos simulados de tránsito ($DE \sim \text{Uniforme}(7, 9)$ días).

### 📦 Costo de Almacenamiento Sobrante (CSOB)
La profesora destacó que el costo de almacenamiento sobrante tiene un **alto costo financiero**. En la simulación:
* Se aplica una penalización diaria de `CSOB = $5.00` por cada unidad de stock que arribe al depósito y supere la capacidad máxima establecida (`MAX_CAP = 10`).
* En la **Situación Actual**, este costo promedio resulta muy bajo (~$0.03) debido a que la política de pedidos "a ojo" tiende a subabastecer el sistema. Sin embargo, en políticas con pedidos de tamaño fijo o entregas desfasadas, representa una variable de alto riesgo crítico.

### 🎯 Optimización del Punto de Reorden (SR)
El script realiza un barrido automático de $SR$ entre $0$ y $MAX\_CAP - 1$ aplicando la técnica de **Números Aleatorios Comunes (Common Random Numbers - CRN)** con el fin de realizar una comparación estadísticamente justa compartiendo la misma secuencia pseudoaleatoria inicial. 

---

## 📊 Últimos Resultados Obtenidos (1.500 Réplicas)

Bajo los parámetros estándar ($CEP = \$100$, $CVP = \$250$, $CALM = \$2$, $CSOB = \$5$):

### 1. Comparativa de Escenarios del Modelo Ideal
* **SR = 0 (Sin reorden)**: Costo promedio $\approx \$26.766,90$ (excesivas ventas perdidas).
* **SR = 4**: Costo promedio $\approx \$15.337,10$.
* **SR = 7 ⭐ (ÓPTIMO)**: Costo promedio **$\approx \$13.292,24$** (mínimo costo financiero).

### 2. Comparativa Final: Situación Actual vs. Modelo Ideal Óptimo ($SR = 7$)

| Métrica (Valores Medios) | Situación Actual | Modelo Ideal ($SR = 7$) | Ahorro / Beneficio |
| :--- | :---: | :---: | :---: |
| Costo Almacenamiento Regular | $\$210,44$ | $\$214,31$ | $-\$3,87$ (Costo marginal adicional) |
| Costo Almacenamiento Sobrante | $\$0,03$ | $N/A$ | — |
| Costo Ventas Perdidas | $\$15.239,67$ | $\$12.177,67$ | **$-\$3.062,00$** (Menor quiebre de stock) |
| Costo Emisión de Pedidos | $\$1.100,00$ | $\$900,27$ | **$-\$199,73$** (Menos pedidos y más eficientes) |
| **Costo Total (CTF)** | **$\$16.550,14$** | **$\$13.292,24$** | **$-\$3.257,90$ (Ahorro del $19.7\%$)** |
| Unidades Perdidas | $60,96$ | $48,71$ | $-12,25$ unidades $(-20.1\%)$ |
| Pedidos Realizados | $11,00$ | $9,00$ | $-2,00$ pedidos |

### Conclusión Principal
El pasaje de una revisión semanal con pedidos "a ojo" a una política de **Revisión Continua con un Punto de Reorden ($SR = 7$)** permite a la distribuidora **S&M** reducir sus costos logísticos globales en casi un **$20\%$**, disminuyendo notablemente las ventas perdidas ante quiebres de stock.


