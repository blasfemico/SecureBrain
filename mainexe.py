import tkinter as tk
from tkinter import ttk, messagebox
from MSS.motion_detection import start_motion_detection, stop_motion_detection
import logging
import os

log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_folder, "mainexe.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

notifications_enabled = True

def toggle_notifications():
    """Habilitar o deshabilitar las notificaciones."""
    global notifications_enabled
    notifications_enabled = not notifications_enabled
    status = "habilitadas" if notifications_enabled else "deshabilitadas"
    messagebox.showinfo("Notificaciones", f"Las notificaciones ahora están {status}.")
    logging.info(f"Notificaciones {status} por el usuario.")

def update_logs():
    """Actualizar los logs en tiempo real en la interfaz."""
    try:
        with open(os.path.join(log_folder, "motion_detection.log"), "r") as file:
            logs = file.readlines()[-10:]  # Mostrar los últimos 10 logs
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, "".join(logs))
    except FileNotFoundError:
        log_text.insert(tk.END, "No hay logs disponibles todavía.")
    root.after(2000, update_logs)  # Actualizar logs cada 2 segundos

def start_detection():
    """Iniciar la detección de movimiento."""
    logging.info("Iniciando detección de movimiento.")
    start_motion_detection()
    update_status("Estado: Detectando", "green")
    messagebox.showinfo("Detección", "La cámara ahora está mostrando el feed en tiempo real.")

def stop_detection():
    """Detener la detección de movimiento."""
    logging.info("Deteniendo detección de movimiento.")
    stop_motion_detection()
    update_status("Estado: Detenido", "red")

def update_status(message, color):
    """Actualizar el estado en la interfaz."""
    status_label.config(text=message, fg=color)

def save_configuration():
    """Guardar la configuración del sistema."""
    try:
        min_time = int(entry_min_time.get())
        sensitivity = int(entry_sensitivity.get())

        with open(os.path.join(log_folder, "config.txt"), "w") as file:
            file.write(f"Tiempo mínimo visible: {min_time} segundos\n")
            file.write(f"Sensibilidad: {sensitivity}\n")
        
        messagebox.showinfo("Configuración", "Configuración guardada correctamente.")
        logging.info("Nueva configuración guardada: Tiempo mínimo = %d seg, Sensibilidad = %d", min_time, sensitivity)
    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce valores numéricos válidos.")

# Interfaz gráfica
root = tk.Tk()
root.title("Sistema de Seguridad Mejorado")
root.geometry("900x700")

# Estado del sistema
status_label = tk.Label(root, text="Estado: Inactivo", font=("Helvetica", 14), fg="red")
status_label.pack(pady=10)

# Botones de control
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

ttk.Button(button_frame, text="Iniciar Detección", command=start_detection).grid(row=0, column=0, padx=10)
ttk.Button(button_frame, text="Detener Detección", command=stop_detection).grid(row=0, column=1, padx=10)
ttk.Button(button_frame, text="Habilitar/Deshabilitar Notificaciones", command=toggle_notifications).grid(row=0, column=2, padx=10)

# Configuración del sistema
config_frame = tk.LabelFrame(root, text="Configuración", padx=10, pady=10)
config_frame.pack(pady=20, fill="x")

tk.Label(config_frame, text="Tiempo mínimo visible (segundos):").grid(row=0, column=0, sticky="w")
entry_min_time = ttk.Entry(config_frame)
entry_min_time.grid(row=0, column=1)

tk.Label(config_frame, text="Sensibilidad:").grid(row=0, column=2, sticky="w")
entry_sensitivity = ttk.Entry(config_frame)
entry_sensitivity.grid(row=0, column=3)

ttk.Button(config_frame, text="Guardar Configuración", command=save_configuration).grid(row=1, column=0, columnspan=4, pady=10)

# Logs en tiempo real
log_frame = tk.LabelFrame(root, text="Logs en Tiempo Real", padx=10, pady=10)
log_frame.pack(pady=20, fill="both", expand=True)

log_text = tk.Text(log_frame, height=10, state="normal")
log_text.pack(fill="both", expand=True)

# Actualizar logs periódicamente
update_logs()

# Iniciar la aplicación
root.mainloop()
