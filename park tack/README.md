# ParkTrack — Primera versión del desarrollo

Evidencia de que el sistema descrito en el PIA ya comenzó a desarrollarse.

## 1. Estructura de datos definida

Dos tablas creadas en SQLite (`db.py`), coincidentes con la sección 6 del PIA:

```sql
CREATE TABLE Configuracion (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    capacidad_total INTEGER NOT NULL,
    tarifa_por_hora REAL NOT NULL
);

CREATE TABLE Transacciones (
    folio INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT NOT NULL,
    hora_entrada TEXT NOT NULL,
    hora_salida TEXT,
    monto REAL,
    estado TEXT NOT NULL DEFAULT 'activo'
);
```

## 2. Conexión con base de datos

`db.py` crea y prueba la conexión local a SQLite (`parktrack.db`), y carga
`Configuracion` con los valores iniciales: **capacidad_total = 50**,
**tarifa_por_hora = $15**.

## 3. Módulo principal / procesamiento inicial (`logic.py`)

Funciones base implementadas y **probadas**:

| Función | Qué hace |
|---|---|
| `registrar_entrada(placa)` | Crea el folio, guarda hora de entrada, valida capacidad disponible |
| `registrar_salida(folio)` | Calcula tiempo transcurrido y monto, libera el espacio |
| `calcular_tarifa(hora_entrada, hora_salida)` | Cobra por hora o fracción (redondeo hacia arriba) |
| `espacios_disponibles()` | Capacidad total − vehículos con estado `activo` |
| `reporte_ingresos()` | Suma de montos de transacciones cerradas |
| `historial_vehiculos()` | Consulta de transacciones por placa o completas |

## 4. Interfaz básica (`main.py`)

Ventana Tkinter con las tres opciones del PIA — **Registrar entrada**,
**Registrar salida**, **Ver disponibilidad** — más Reporte de ingresos e
Historial. Compila sin errores (`python3 -m py_compile main.py`); requiere
un entorno con `tkinter`/display para ejecutarse visualmente.

## 5. Simulación básica (`simulacion.py`)

Ejercita el flujo completo por consola, sin necesitar la interfaz gráfica.
**Salida real de la ejecución:**

```
1) Base de datos inicializada (Configuracion + Transacciones).
   Capacidad total: 50 espacios | Tarifa: $15.0/hora
------------------------------------------------------------
2) Disponibilidad inicial: 50 espacios libres.
------------------------------------------------------------
3) Registrando entradas de 3 vehículos...
   -> Entrada registrada: placa=ABC-123, folio=1
   -> Entrada registrada: placa=XYZ-987, folio=2
   -> Entrada registrada: placa=JLM-456, folio=3
------------------------------------------------------------
4) Disponibilidad tras 3 entradas: 47 espacios libres (esperado 47).
------------------------------------------------------------
5) Simulando el paso del tiempo para el primer vehículo (2.5 horas)...
------------------------------------------------------------
6) Registrando salida del primer vehículo...
   Monto a cobrar: $45.00 (2h30 -> se cobran 3 horas por fracción, 3 x $15 = $45.00)
------------------------------------------------------------
7) Disponibilidad tras la salida: 48 espacios libres (esperado 48).
------------------------------------------------------------
8) Reporte de ingresos actual:
   Folio 1 | ABC-123 | $45.00
   Ingresos totales: $45.00
------------------------------------------------------------
9) Historial de vehículos registrados:
   Folio 2 | XYZ-987 | estado=activo
   Folio 3 | JLM-456 | estado=activo
   Folio 1 | ABC-123 | estado=cerrado
------------------------------------------------------------
10) Prueba de límite de capacidad...
   Vehículo #49 rechazado correctamente: No hay espacios disponibles.
   Se registraron 48 vehículos adicionales antes de saturar el estacionamiento.
   Disponibilidad final: 0 espacios libres.
------------------------------------------------------------
Simulación completada sin errores.
```

Esto confirma: cálculo correcto de tarifa por hora/fracción, descuento y
liberación de espacios, generación de reporte y respeto al límite de
capacidad configurado.

## 6. Repositorio y código inicial

Se inicializó un repositorio git local con el primer commit, incluyendo el
esquema de la base de datos y las funciones base:

```
commit e1d1aed
Primera version: estructura de datos, conexion SQLite, modulo principal e interfaz basica en Tkinter

 .gitignore    |   3 +
 db.py         |  77 ++
 logic.py      | 185 ++
 main.py       | 128 ++
 simulacion.py | 119 ++
 5 files changed, 512 insertions(+)
```
Para subirlo a GitHub: `git remote add origin <URL_DEL_REPO> && git push -u origin main`.

## Cómo ejecutar

```bash
cd park_track
python3 simulacion.py   # evidencia por consola (no requiere entorno gráfico)
python3 main.py         # interfaz Tkinter (requiere entorno con display)
```

## Tecnologías usadas
Python 3, Tkinter, SQLite (`sqlite3`), Git — tal como se definió en la
sección 5 del PIA.
