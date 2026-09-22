"""
logic.py
Módulo principal de procesamiento - ParkTrack
Implementa las funciones base descritas en la sección 6 del PIA:
    - registrar_entrada(placa)
    - registrar_salida(folio)
    - calcular_tarifa(hora_entrada, hora_salida)
    - espacios_disponibles()
"""

import math
from datetime import datetime
from db import conectar_db


FORMATO_HORA = "%Y-%m-%d %H:%M:%S"


def calcular_tarifa(hora_entrada, hora_salida, tarifa_por_hora):
    """
    Calcula el monto a cobrar según tiempo transcurrido (por hora o fracción).
    hora_entrada / hora_salida: strings en FORMATO_HORA o datetime.
    """
    if isinstance(hora_entrada, str):
        hora_entrada = datetime.strptime(hora_entrada, FORMATO_HORA)
    if isinstance(hora_salida, str):
        hora_salida = datetime.strptime(hora_salida, FORMATO_HORA)

    segundos = (hora_salida - hora_entrada).total_seconds()
    if segundos < 0:
        raise ValueError("La hora de salida no puede ser anterior a la hora de entrada.")

    horas_fraccion = segundos / 3600
    # Se cobra por hora o fracción: siempre se redondea hacia arriba,
    # con un mínimo de 1 hora.
    horas_a_cobrar = max(1, math.ceil(horas_fraccion))
    monto = round(horas_a_cobrar * tarifa_por_hora, 2)
    return monto


def espacios_disponibles(conn=None):
    """Regresa el conteo actual de espacios libres (capacidad_total - ocupados)."""
    cerrar = False
    if conn is None:
        conn = conectar_db()
        cerrar = True

    cfg = conn.execute("SELECT capacidad_total FROM Configuracion WHERE id = 1;").fetchone()
    ocupados = conn.execute(
        "SELECT COUNT(*) AS n FROM Transacciones WHERE estado = 'activo';"
    ).fetchone()["n"]

    disponibles = cfg["capacidad_total"] - ocupados

    if cerrar:
        conn.close()
    return disponibles


def registrar_entrada(placa, conn=None):
    """
    Registra la entrada de un vehículo: crea el folio y guarda hora de entrada.
    Resta un espacio disponible (vía estado='activo').
    Regresa el folio generado.
    """
    cerrar = False
    if conn is None:
        conn = conectar_db()
        cerrar = True

    placa = placa.strip().upper()
    if not placa:
        raise ValueError("La placa no puede estar vacía.")

    if espacios_disponibles(conn) <= 0:
        if cerrar:
            conn.close()
        raise RuntimeError("No hay espacios disponibles.")

    hora_entrada = datetime.now().strftime(FORMATO_HORA)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Transacciones (placa, hora_entrada, estado) VALUES (?, ?, 'activo');",
        (placa, hora_entrada),
    )
    conn.commit()
    folio = cur.lastrowid

    if cerrar:
        conn.close()
    return folio


def registrar_salida(folio, conn=None):
    """
    Registra la salida de un vehículo: calcula tiempo transcurrido y monto a cobrar,
    libera el espacio y guarda la transacción completa.
    Regresa un dict con folio, placa, hora_entrada, hora_salida y monto.
    """
    cerrar = False
    if conn is None:
        conn = conectar_db()
        cerrar = True

    fila = conn.execute(
        "SELECT * FROM Transacciones WHERE folio = ? AND estado = 'activo';", (folio,)
    ).fetchone()

    if fila is None:
        if cerrar:
            conn.close()
        raise ValueError(f"Folio {folio} no encontrado o ya fue cerrado.")

    cfg = conn.execute("SELECT tarifa_por_hora FROM Configuracion WHERE id = 1;").fetchone()
    hora_salida_dt = datetime.now()
    hora_salida = hora_salida_dt.strftime(FORMATO_HORA)
    monto = calcular_tarifa(fila["hora_entrada"], hora_salida, cfg["tarifa_por_hora"])

    conn.execute(
        "UPDATE Transacciones SET hora_salida = ?, monto = ?, estado = 'cerrado' WHERE folio = ?;",
        (hora_salida, monto, folio),
    )
    conn.commit()

    resultado = {
        "folio": folio,
        "placa": fila["placa"],
        "hora_entrada": fila["hora_entrada"],
        "hora_salida": hora_salida,
        "monto": monto,
    }

    if cerrar:
        conn.close()
    return resultado


def reporte_ingresos(conn=None, desde=None, hasta=None):
    """
    Genera un reporte de ingresos (suma de montos de transacciones cerradas)
    en un rango de fechas opcional (strings FORMATO_HORA).
    """
    cerrar = False
    if conn is None:
        conn = conectar_db()
        cerrar = True

    query = "SELECT folio, placa, hora_entrada, hora_salida, monto FROM Transacciones WHERE estado = 'cerrado'"
    params = []
    if desde:
        query += " AND hora_salida >= ?"
        params.append(desde)
    if hasta:
        query += " AND hora_salida <= ?"
        params.append(hasta)
    query += " ORDER BY hora_salida;"

    filas = conn.execute(query, params).fetchall()
    total = sum(f["monto"] for f in filas) if filas else 0.0

    if cerrar:
        conn.close()
    return {"transacciones": [dict(f) for f in filas], "total_ingresos": round(total, 2)}


def historial_vehiculos(conn=None, placa=None):
    """Consulta el historial de vehículos registrados, opcionalmente filtrado por placa."""
    cerrar = False
    if conn is None:
        conn = conectar_db()
        cerrar = True

    if placa:
        filas = conn.execute(
            "SELECT * FROM Transacciones WHERE placa = ? ORDER BY hora_entrada DESC;",
            (placa.strip().upper(),),
        ).fetchall()
    else:
        filas = conn.execute(
            "SELECT * FROM Transacciones ORDER BY hora_entrada DESC;"
        ).fetchall()

    if cerrar:
        conn.close()
    return [dict(f) for f in filas]
