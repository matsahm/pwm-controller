#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import RPi.GPIO as GPIO
import time
from threading import Thread, Event
import configparser

# Config-Datei einlesen
config = configparser.ConfigParser()
config.read('config.ini')
gpio_int = int(config['PWM']['GPIOPin'])
frequency_int = int(config['PWM']['Frequency'])
min_var = config['DEFAULT']['MinValue']
max_var = config['DEFAULT']['MaxValue']
steps_var = config['DEFAULT']['StepsValue']
sleep_var = config['DEFAULT']['SleepValue']
fontfamily_var = config['DESIGN']['FontFamily']
fontsize_label_int = int(config['DESIGN']['FontSizeLabel'])
circle_size = fontsize_label_int * 1.3

# GPIO initialisieren
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_int, GPIO.OUT)
p = GPIO.PWM(gpio_int, frequency_int)
p.start(0)

# Globaler Thread
pwm_thread = None

# Event, um den PWM-Thread anzuhalten
pause_event = Event()

def update_gui(args):
    dc, status = args
    if dc is not None:
        value_text.config(text=str(dc))
    if status is not None:
        status_text.config(text=status)

def update_pwm():
    while not pause_event.is_set():
        try:
            min_value = int(min_entry.get())
            max_value = int(max_entry.get())
            steps_value = int(steps_entry.get())
            sleep_time = float(speed_entry.get())
        except ValueError:
            status_text.config(text="Ungültige Eingabe!")
            return

        # PWM aktualisieren
        for dc in range(min_value, max_value + 1, steps_value):
            if pause_event.is_set():
                break
            p.ChangeDutyCycle(dc)
            root.after(0, update_gui, (dc, None))
            time.sleep(sleep_time)
            update_color(dc)
        for dc in range(max_value, min_value - 1, -steps_value):
            if pause_event.is_set():
                break
            p.ChangeDutyCycle(dc)
            root.after(0, update_gui, (dc, None))
            time.sleep(sleep_time)
            update_color(dc)

def update_color(value):
    # Berechne die Farbe zwischen Schwarz (0) und Rot (100)
    red = int(255 * (value / 100))
    color = f'#{red:02x}0000'
    canvas.itemconfig(circle, fill=color)

def start_pwm():
    global pwm_thread
    if pwm_thread is None:
        pwm_thread = Thread(target=update_pwm)
        pwm_thread.start()
        root.after(0, update_gui, (None, "PWM läuft"))
    elif not pwm_thread.is_alive():
        pause_event.clear()
        pwm_thread = Thread(target=update_pwm)
        pwm_thread.start()
        root.after(0, update_gui, (None, "PWM läuft"))

def pause_pwm():
    pause_event.set()
    root.after(0, update_gui, (None, "PWM pausiert"))

def stop_pwm():
    pause_event.set()
    p.ChangeDutyCycle(0)
    value_text.config(text="0")
    update_color(0)
    root.after(0, update_gui, (0, "PWM gestoppt"))

def quit_program():
    try:
        pause_event.set()
        p.stop()
    except RuntimeError as e:
        print(f"Fehler beim Anhalten von PWM: {e}")
    finally:
        GPIO.cleanup()
        root.destroy()

# Tkinter GUI initialisieren
root = tk.Tk()
root.title("PWM Controller")

# Schriftgrößen definieren
label_font = tkFont.Font(family=fontfamily_var, size=fontsize_label_int)

# Eingabefelder
min_label = ttk.Label(root, text="Min:", font=label_font)
min_label.grid(row=0, column=0, padx=10, pady=10)
min_entry = ttk.Entry(root, font=label_font)
min_entry.insert(0, min_var)
min_entry.grid(row=0, column=1, padx=10, pady=10, columnspan=2)
max_label = ttk.Label(root, text="Max:", font=label_font)
max_label.grid(row=1, column=0, padx=10, pady=10)
max_entry = ttk.Entry(root, font=label_font)
max_entry.insert(0, max_var)
max_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=2)
steps_label = ttk.Label(root, text="Schritte:", font=label_font)
steps_label.grid(row=2, column=0, padx=10, pady=10)
steps_entry = ttk.Entry(root, font=label_font)
steps_entry.insert(0, steps_var)
steps_entry.grid(row=2, column=1, padx=10, pady=10, columnspan=2)
speed_label = ttk.Label(root, text="Pause:", font=label_font)
speed_label.grid(row=3, column=0, padx=10, pady=10)
speed_entry = ttk.Entry(root, font=label_font)
speed_entry.insert(0, sleep_var)
speed_entry.grid(row=3, column=1, padx=10, pady=10, columnspan=2)

# Ausgabefelder
status_label = ttk.Label(root, text="Status:", font=label_font)
status_label.grid(row=4, column=0, padx=10, pady=10)
status_text = ttk.Label(root, text="Bereit", font=label_font)
status_text.grid(row=4, column=1, padx=10, pady=10, columnspan=2)
value_label = ttk.Label(root, text="Wert:", font=label_font)
value_label.grid(row=5, column=0, padx=10, pady=10)
value_text = ttk.Label(root, text="0", font=label_font)
value_text.grid(row=5, column=1, padx=10, pady=10)
canvas = tk.Canvas(root, width=circle_size, height=circle_size)
canvas.grid(column=2, row=5)
circle = canvas.create_oval(0, 0, circle_size, circle_size, fill='black')

# Knöpfe
start_button = ttk.Button(root, text="Start", command=start_pwm)
start_button.grid(row=6, column=0, padx=10, pady=10)
pause_button = ttk.Button(root, text="Pause", command=pause_pwm)
pause_button.grid(row=6, column=1, padx=10, pady=10)
stop_button = ttk.Button(root, text="Stopp", command=stop_pwm)
stop_button.grid(row=6, column=2, padx=10, pady=10)
quit_button = ttk.Button(root, text="Beenden", command=quit_program)
quit_button.grid(row=7, column=1, padx=10, pady=10)

# Starte die Tkinter-Ereignisschleife
root.mainloop()

# Bereinige GPIO beim Schließen des Fensters
GPIO.cleanup()
