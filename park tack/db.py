"""
db.py
Módulo de Acceso a Datos - ParkTrack
Conexión con SQLite y creación de la estructura de datos definida
en la sección 6 del PIA: tablas Transacciones y Configuracion.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "parktrack.db")


def conectar_db():
    """Abre (o crea) la base de datos local SQLite y regresa la conexión."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def crear_tablas(conn):
    """Crea las tablas iniciales si no existen."""
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Configuracion (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            capacidad_total INTEGER NOT NULL,
            tarifa_por_hora REAL NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Transacciones (
            folio INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            hora_entrada TEXT NOT NULL,
            hora_salida TEXT,
            monto REAL,
            estado TEXT NOT NULL DEFAULT 'activo'
        );
    """)
    conn.commit()


def inicializar_configuracion(conn, capacidad_total=50, tarifa_por_hora=15.0):
    """
    Carga la fila única de Configuracion si aún no existe.
    Valores por defecto según el PIA: 50 espacios, $15/hora.
    """
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM Configuracion;")
    existe = cur.fetchone()["n"] > 0
    if not existe:
        cur.execute(
            "INSERT INTO Configuracion (id, capacidad_total, tarifa_por_hora) VALUES (1, ?, ?);",
            (capacidad_total, tarifa_por_hora),
        )
        conn.commit()


def inicializar_db():
    """Punto de entrada único: conecta, crea tablas y carga configuración inicial."""
    conn = conectar_db()
    crear_tablas(conn)
    inicializar_configuracion(conn)
    return conn


if __name__ == "__main__":
    conn = inicializar_db()
    print(f"Base de datos creada/conectada en: {DB_PATH}")
    cfg = conn.execute("SELECT * FROM Configuracion;").fetchone()
    print(f"Configuración cargada -> capacidad_total: {cfg['capacidad_total']}, "
          f"tarifa_por_hora: ${cfg['tarifa_por_hora']}/hora")
    conn.close()
