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
├── Tablas - Trasnformada Inversa de corrido.csv # Datos de demora en días corridos
├── Tablas - Trasnformada Inversa.csv # Datos de demora originales
├── Tablas - nro_pseudo.csv       # Semillas y parámetros del generador congruencial
├── Tablas - Mueble-Camilo.csv    # Datos históricos reales del Mueble Camilo
│
├── datos.py                      # Módulo de carga de parámetros y CSVs (Pandas)
├── simulacion_actual.py          # Lógica de simulación de la situación actual (pedido los lunes)
├── simulacion_ideal.py           # Lógica de simulación del modelo ideal (revisión continua Q,R)
├── main.py                       # Punto de entrada de la simulación, optimización y comparativa
├── test_suite.py                 # Suite de pruebas unitarias
├── crear_excel_muebles.py        # Generación del Excel de verificación para Muebles Camilo
├── crear_excel_referencia.py     # Generación del Excel de verificación para Powerade (referencia)
└── README.md                     # Documentación general del proyecto (este archivo)
```

---

## 🛠️ Metodología Utilizada

### 1. Generación de Números Pseudoaleatorios
Se utiliza el **Método Congruencial Mixto** parametrizado con los valores del archivo `Tablas - nro_pseudo.csv`:
$$X_{n+1} = (a \cdot X_n + c) \pmod{m}$$
$$r_n = \frac{X_n}{m}$$
Con los valores específicos de la cátedra ($X_0 = 1778, a = 2999, c = 7853, m = 14729$), el generador tiene un período matemático de **510** números antes de repetir el ciclo completo.

### 2. Generación de Variables Aleatorias
* **Demanda Diaria**: Se modela usando una distribución de **Poisson ($\lambda = 1.54$)** implementada mediante el **Método de Rechazo** utilizando pares de números aleatorios uniformes.
* **Demora del Proveedor (DE)**: Se modela usando una distribución **Uniforme discreta** implementada mediante la **Transformada Inversa**.

### 3. Pruebas Estadísticas Realizadas
Para garantizar la calidad de los números generados, el sistema ejecuta 5 pruebas estadísticas sobre la secuencia generada:
1. **Prueba de Media** (Z)
2. **Prueba de Varianza** ($\chi^2$)
3. **Prueba de Uniformidad** (Bondad de Ajuste $\chi^2$)
4. **Prueba de Independencia — Corrida Arriba y Abajo** (Z)
5. **Prueba de Independencia — Corrida Arriba y Abajo de la Media** (Z)

> [!NOTE]
> Debido a que la simulación completa genera más de 280.000 números y el generador LCG tiene un período de 510, evaluar la secuencia acumulada completa provocaría el rechazo inevitable en las pruebas de independencia por la ciclicidad periódica. Por lo tanto, el software evalúa los **primeros 500 números generados** (menos de un ciclo completo), aprobando con éxito las **5/5 pruebas (100% de aceptación)**.

---

## 🚀 Instrucciones de Ejecución

### Requisitos Previos
Asegúrate de tener instaladas las librerías necesarias ejecutando:
```bash
pip install pandas scipy openpyxl
```

### Ejecutar la Simulación y Comparativa Financiera
Para correr el modelo de la situación actual y desplegar la comparativa de optimización frente al modelo ideal junto con las pruebas estadísticas, ejecuta:
```bash
python main.py
```

### Ejecutar la Suite de Pruebas Unitarias
Para correr los tests automatizados que validan los generadores individuales y las pruebas estadísticas:
```bash
python test_suite.py
```

### Generar Reportes Excel de Validación
Para crear las planillas de verificación de frecuencia teórica vs. observada y cálculo de error promedio:
```bash
# Para el Mueble Camilo (real de S&M)
python crear_excel_muebles.py

# Para el caso de referencia (Powerade)
python crear_excel_referencia.py
```

---

## 📊 Configuración de Variables en `main.py`

En la parte superior de `main.py` se definen las variables operativas y financieras realistas en **Pesos Argentinos (ARS)** para un análisis coherente con el negocio de S&M en el Chaco:

```python
# Cantidad de Réplicas (Corridas independientes)
N_REPLICACIONES = 1500

# Costos (en ARS)
CEP      = 35_000.0    # Costo logístico/flete y emisión ($/pedido)
CVP      = 71_000.0    # Costo de venta perdida ($/unidad - margen neto perdido)
CALM     = 800.0       # Costo de almacenamiento regular ($/unidad·día)
CSOB     = 2_000.0     # Costo de almacenamiento sobrante ($/unidad·día)

# Valores comerciales del mueble Camilo
CUN      = 234_000.0   # Costo de compra unitario al proveedor ($)
CV       = 305_000.0   # Precio de venta al cliente unitario ($)
PRESUP_0 = 1_000_000.0 # Presupuesto de caja inicial ($)

# Parámetros de Simulación
TF      = 70           # Tiempo final de simulación (días corridos)
MAX_CAP = 10           # Capacidad máxima del depósito
ST_0    = 7            # Stock inicial
ALFA    = 0.05         # Nivel de significancia para pruebas estadísticas
```

---

## 📈 Comparativa de Modelos: Actual vs. Ideal

Al ejecutar la simulación, `main.py` corre de forma secuencial:
1. **Situación Actual**: Revisión y pedido **únicamente los lunes** (días corridos, donde fines de semana tienen ventas nulas). El tamaño del pedido se decide "a ojo" intentando llenar el depósito hasta `MAX_CAP` pero limitando la compra estrictamente según la disponibilidad del presupuesto (`PRESUP`), asegurando que no se compre de más ni se quede en caja negativa.
2. **Modelo Ideal**: Revisión diaria (continua) con reorden cuando $ST < SR$. Si se cumple y no hay pedidos pendientes (`PE == 0`), se ordena para llenar el depósito ($TP = MAX\_CAP - ST$). Solo puede haber un pedido en tránsito a la vez.

---

## 📊 Resultados Obtenidos (1.500 Réplicas)

Bajo los parámetros de costos sincerados (ARS), los promedios de la simulación arrojan el siguiente panorama:

### 1. Comparativa de Escenarios del Modelo Ideal
* **SR = 0 (Sin reorden)**: Costo promedio $\approx \$5.022.880,13$ (70.6 unidades perdidas).
* **SR = 2 ⭐ (ÓPTIMO en Modelo Ideal)**: Costo promedio **$\approx \$3.150.999,87$** (41.11 unidades perdidas).
* **SR = 9**: Costo promedio $\approx \$3.512.299,33$ (45.9 unidades perdidas).

*Nota: En el modelo ideal, aumentar el SR por encima de 2 diluye el tamaño de los pedidos y, debido al bloqueo de "un solo pedido en tránsito a la vez" con 7-9 días de demora, incrementa drásticamente los quiebres de stock.*

### 2. Comparativa Final: Situación Actual vs. Modelo Ideal Óptimo ($SR = 2$)

| Métrica (Valores Medios) | Situación Actual (Semanal Lunes) | Modelo Ideal ($SR = 2$) | Diferencia (Ideal vs. Actual) |
| :--- | :---: | :---: | :---: |
| Costo Almacenamiento Regular | $\$143.564,80$ | $\$85.984,53$ | $-\$57.580,27$ *(Ideal ahorra espacio)* |
| Costo Almacenamiento Sobrante | $\$12.009,33$ | *No aplica* | $-\$12.009,33$ |
| Costo Ventas Perdidas | $\$1.393.540,67$ | $\$2.918.715,33$ | **$+\$1.525.174,66$ ❌** *(Ideal duplica pérdidas)* |
| Costo Emisión de Pedidos | $\$358.726,67$ | $\$146.300,00$ | $-\$212.426,67$ *(Ideal pide menos)* |
| **Costo Total (CTF)** | **$\$1.907.841,47$** | **$\$3.150.999,87$** | **$+\$1.243.158,40$ ❌** |
| Unidades Perdidas | $19,63$ | $41,11$ | $+21,48$ unidades |
| Pedidos Realizados | $10,25$ | $4,18$ | $-6,07$ pedidos |

### 💡 Conclusión Principal del Proyecto
Con costos sinceros, **la Situación Actual es significativamente superior al Modelo Ideal propuesto (ahorro del 39.4%)**. 

Esto expone un problema estructural del modelo ideal: la regla de **un solo pedido en tránsito a la vez** actúa como un cuello de botella logístico insalvable cuando el proveedor tarda entre 7 y 9 días. Al no poder realizar pedidos superpuestos, el modelo ideal sufre quiebres de stock masivos. La **Situación Actual**, al pedir todas las semanas de forma superpuesta, mantiene un flujo constante de stock que protege las ventas y la rentabilidad neta del negocio.
