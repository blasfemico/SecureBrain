import tkinter as tk
from tkinter import ttk
from MSS.motion_detection import start_motion_detection, stop_motion_detection
import cv2
from PIL import Image, ImageTk

camera = None
video_running = False

def start_camera():
    global camera, video_running
    if not video_running:
        camera = cv2.VideoCapture(0)
        video_running = True
        update_video_feed()

def stop_camera():
    global camera, video_running
    video_running = False
    if camera:
        camera.release()
        video_canvas.delete("all")

def update_video_feed():
    global camera, video_running
    if video_running:
        ret, frame = camera.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            video_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            video_canvas.image = imgtk
        root.after(10, update_video_feed)

root = tk.Tk()
root.title("Sistema de Detección de Movimiento")
root.geometry("800x600")

video_canvas = tk.Canvas(root, width=640, height=480, bg="black")
video_canvas.pack()

button_frame = tk.Frame(root)
button_frame.pack()

ttk.Button(button_frame, text="Iniciar Cámara", command=start_camera).grid(row=0, column=0, padx=10, pady=10)
ttk.Button(button_frame, text="Detener Cámara", command=stop_camera).grid(row=0, column=1, padx=10, pady=10)

root.mainloop()
