#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO

# Konfiguriere den GPIO-Pin
GPIO_PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

# Initialisiere PWM
pwm = GPIO.PWM(GPIO_PIN, 50)
pwm_value = 0

def update_pwm(val):
    global pwm_value
    pwm_value = round(float(val))
    pwm.ChangeDutyCycle(pwm_value)
    label.config(text=f"Aktueller Wert: {pwm_value} %")
    update_color(pwm_value)

def update_color(value):
    # Berechne die Farbe zwischen Schwarz (0) und Rot (100)
    red = int(255 * (value / 100))
    color = f'#{red:02x}0000'
    canvas.itemconfig(circle, fill=color)

def start_pwm():
    pwm.start(pwm_value)

def stop_pwm():
    pwm.stop()

def close_program():
    pwm.stop()
    GPIO.cleanup()
    root.destroy()

# Erstelle die GUI
root = tk.Tk()
root.title("PWM Slider")

mainframe = ttk.Frame(root, padding="6 6 24 24")
mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

slider = ttk.Scale(mainframe, from_=0, to=100, orient=tk.HORIZONTAL, command=update_pwm, length=300)
slider.grid(column=0, row=0, sticky=(tk.W, tk.E))

label = ttk.Label(mainframe, text="Aktueller Wert: 0 %")
label.grid(column=0, row=1, sticky=(tk.W, tk.E))

start_button = ttk.Button(mainframe, text="Start", command=start_pwm)
start_button.grid(column=0, row=2, sticky=tk.W)

stop_button = ttk.Button(mainframe, text="Stop", command=stop_pwm)
stop_button.grid(column=0, row=2)

close_button = ttk.Button(mainframe, text="Beenden", command=close_program)
close_button.grid(column=0, row=2, sticky=tk.E)

canvas = tk.Canvas(mainframe, width=20, height=20)
canvas.grid(column=0, row=1, sticky=tk.E)
circle = canvas.create_oval(0, 0, 20, 20, fill='black')

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=10, pady=10)

root.mainloop()

