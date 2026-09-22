"""
main.py
Interfaz básica - ParkTrack
Pantalla inicial en Tkinter con las tres opciones descritas en el PIA:
    - Registrar entrada
    - Registrar salida
    - Ver disponibilidad

También incluye acceso a Reporte de ingresos e Historial, ya soportados
por el módulo de lógica (logic.py), como parte de la primera versión.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from db import inicializar_db
from logic import (
    registrar_entrada,
    registrar_salida,
    espacios_disponibles,
    reporte_ingresos,
    historial_vehiculos,
)


class ParkTrackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ParkTrack - Sistema de Estacionamiento")
        self.geometry("420x320")
        self.resizable(False, False)

        self.conn = inicializar_db()

        self._construir_interfaz()
        self._actualizar_disponibilidad()

    def _construir_interfaz(self):
        titulo = tk.Label(self, text="ParkTrack", font=("Arial", 20, "bold"))
        titulo.pack(pady=(20, 5))

        subtitulo = tk.Label(self, text="Control de entradas, salidas y tarifas")
        subtitulo.pack(pady=(0, 15))

        self.lbl_disponibilidad = tk.Label(self, text="", font=("Arial", 12))
        self.lbl_disponibilidad.pack(pady=(0, 15))

        ttk.Button(self, text="Registrar entrada", width=30,
                   command=self.accion_registrar_entrada).pack(pady=5)
        ttk.Button(self, text="Registrar salida", width=30,
                   command=self.accion_registrar_salida).pack(pady=5)
        ttk.Button(self, text="Ver disponibilidad", width=30,
                   command=self.accion_ver_disponibilidad).pack(pady=5)
        ttk.Button(self, text="Reporte de ingresos", width=30,
                   command=self.accion_reporte_ingresos).pack(pady=5)
        ttk.Button(self, text="Historial de vehículos", width=30,
                   command=self.accion_historial).pack(pady=5)

    def _actualizar_disponibilidad(self):
        disponibles = espacios_disponibles(self.conn)
        self.lbl_disponibilidad.config(text=f"Espacios disponibles: {disponibles}")

    # ---- Acciones ----

    def accion_registrar_entrada(self):
        placa = simpledialog.askstring("Registrar entrada", "Ingrese la placa del vehículo:")
        if not placa:
            return
        try:
            folio = registrar_entrada(placa, self.conn)
            messagebox.showinfo("Entrada registrada",
                                 f"Folio generado: {folio}\nPlaca: {placa.upper()}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self._actualizar_disponibilidad()

    def accion_registrar_salida(self):
        folio = simpledialog.askinteger("Registrar salida", "Ingrese el folio del vehículo:")
        if folio is None:
            return
        try:
            resultado = registrar_salida(folio, self.conn)
            messagebox.showinfo(
                "Salida registrada",
                f"Placa: {resultado['placa']}\n"
                f"Entrada: {resultado['hora_entrada']}\n"
                f"Salida: {resultado['hora_salida']}\n"
                f"Monto a cobrar: ${resultado['monto']:.2f}"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self._actualizar_disponibilidad()

    def accion_ver_disponibilidad(self):
        self._actualizar_disponibilidad()
        disponibles = espacios_disponibles(self.conn)
        messagebox.showinfo("Disponibilidad", f"Espacios disponibles: {disponibles}")

    def accion_reporte_ingresos(self):
        reporte = reporte_ingresos(self.conn)
        n = len(reporte["transacciones"])
        messagebox.showinfo(
            "Reporte de ingresos",
            f"Transacciones cerradas: {n}\nIngresos totales: ${reporte['total_ingresos']:.2f}"
        )

    def accion_historial(self):
        historial = historial_vehiculos(self.conn)
        if not historial:
            messagebox.showinfo("Historial", "Aún no hay vehículos registrados.")
            return
        texto = "\n".join(
            f"Folio {h['folio']} | {h['placa']} | entrada {h['hora_entrada']} | "
            f"estado {h['estado']}"
            for h in historial[:15]
        )
        messagebox.showinfo("Historial de vehículos (últimos 15)", texto)

    def destroy(self):
        self.conn.close()
        super().destroy()


if __name__ == "__main__":
    app = ParkTrackApp()
    app.mainloop()
