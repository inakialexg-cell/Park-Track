"""
simulacion.py
Simulación básica - ParkTrack
Ejercita el flujo completo (entrada -> disponibilidad -> salida -> tarifa
-> reporte -> historial) sin necesitar la interfaz gráfica, como evidencia
de que el procesamiento del sistema ya funciona de punta a punta.

Uso:
    python simulacion.py
"""

import os
import time
from datetime import datetime, timedelta

from db import inicializar_db, DB_PATH
from logic import (
    registrar_entrada,
    registrar_salida,
    espacios_disponibles,
    reporte_ingresos,
    historial_vehiculos,
    FORMATO_HORA,
)


def linea():
    print("-" * 60)


def main():
    # Empezamos con una base de datos limpia para que la simulación
    # sea repetible.
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = inicializar_db()
    print("1) Base de datos inicializada (Configuracion + Transacciones).")
    cfg = conn.execute("SELECT * FROM Configuracion;").fetchone()
    print(f"   Capacidad total: {cfg['capacidad_total']} espacios | "
          f"Tarifa: ${cfg['tarifa_por_hora']}/hora")
    linea()

    print(f"2) Disponibilidad inicial: {espacios_disponibles(conn)} espacios libres.")
    linea()

    print("3) Registrando entradas de 3 vehículos...")
    placas = ["ABC-123", "xyz-987", "JLM-456"]
    folios = []
    for p in placas:
        folio = registrar_entrada(p, conn)
        folios.append(folio)
        print(f"   -> Entrada registrada: placa={p.upper()}, folio={folio}")
    linea()

    print(f"4) Disponibilidad tras 3 entradas: {espacios_disponibles(conn)} espacios libres "
          f"(esperado {cfg['capacidad_total'] - 3}).")
    linea()

    print("5) Simulando el paso del tiempo para el primer vehículo (2.5 horas)...")
    # Para demostrar el cálculo de tarifa por hora/fracción sin esperar de verdad,
    # ajustamos manualmente la hora_entrada guardada del primer folio.
    hora_pasada = (datetime.now() - timedelta(hours=2, minutes=30)).strftime(FORMATO_HORA)
    conn.execute("UPDATE Transacciones SET hora_entrada = ? WHERE folio = ?;",
                 (hora_pasada, folios[0]))
    conn.commit()
    print(f"   Hora de entrada del folio {folios[0]} ajustada a {hora_pasada} "
          f"(simulando 2h30 de estancia).")
    linea()

    print("6) Registrando salida del primer vehículo...")
    resultado = registrar_salida(folios[0], conn)
    print(f"   Folio: {resultado['folio']}")
    print(f"   Placa: {resultado['placa']}")
    print(f"   Entrada: {resultado['hora_entrada']}")
    print(f"   Salida:  {resultado['hora_salida']}")
    print(f"   Monto a cobrar: ${resultado['monto']:.2f} "
          f"(2h30 -> se cobran 3 horas por fracción, 3 x $15 = $45.00)")
    assert resultado["monto"] == 45.0, "El cálculo de tarifa no coincide con lo esperado."
    linea()

    print(f"7) Disponibilidad tras la salida: {espacios_disponibles(conn)} espacios libres "
          f"(esperado {cfg['capacidad_total'] - 2}).")
    linea()

    print("8) Reporte de ingresos actual:")
    reporte = reporte_ingresos(conn)
    for t in reporte["transacciones"]:
        print(f"   Folio {t['folio']} | {t['placa']} | ${t['monto']:.2f}")
    print(f"   Ingresos totales: ${reporte['total_ingresos']:.2f}")
    linea()

    print("9) Historial de vehículos registrados:")
    for h in historial_vehiculos(conn):
        print(f"   Folio {h['folio']} | {h['placa']} | estado={h['estado']}")
    linea()

    print("10) Prueba de límite de capacidad: intentando registrar más vehículos "
         "que espacios disponibles...")
    disponibles_antes = espacios_disponibles(conn)
    ok = 0
    for i in range(disponibles_antes + 1):
        try:
            registrar_entrada(f"TEST-{i:03d}", conn)
            ok += 1
        except RuntimeError as e:
            print(f"   Vehículo #{i+1} rechazado correctamente: {e}")
            break
    print(f"   Se registraron {ok} vehículos adicionales antes de saturar el estacionamiento.")
    print(f"   Disponibilidad final: {espacios_disponibles(conn)} espacios libres.")
    linea()

    conn.close()
    print("Simulación completada sin errores. Base de datos de prueba en:")
    print(f"  {DB_PATH}")


if __name__ == "__main__":
    main()
