import random
import threading
import time

import mido
from pynput import keyboard

# Variables globales
current_value = None
previous_value = None
derivative = 0
current_scale = 3  # Escala por defecto

# Configuración de salida MIDI
outport = mido.open_output('Puerto MIDI Virtual', virtual=True)


# Función que simula la llamada a la API
def api_call():
    return random.randint(1, 10)


# Actualiza la escala basándose en el cambio del valor de la API
def update_scale():
    global current_value, previous_value, derivative, current_scale
    while True:
        previous_value = current_value
        current_value = api_call()
        if previous_value is not None:
            derivative = current_value - previous_value
            # Ajusta la escala si hay un cambio significativo
            if derivative >= 5:
                current_scale = min(current_scale + 1, 7)
            elif derivative <= -5:
                current_scale = max(current_scale - 1, 1)
        else:
            current_scale = 3  # Escala por defecto al inicio
        print(f"Valor de API: {current_value}, Derivada: {derivative}, Escala actual: {current_scale}")
        time.sleep(10)


# Inicia el hilo para actualizar la escala
scale_thread = threading.Thread(target=update_scale)
scale_thread.daemon = True
scale_thread.start()


# Mapeo de teclas a notas MIDI
def get_note_for_key(key_char, scale):
    key_note_map = {
        's': 0,  # Do
        'd': 2,  # Re
        'f': 4,  # Mi
        'g': 5,  # Fa
        'h': 7,  # Sol
        'j': 9,  # La
        'k': 11,  # Si
    }
    if key_char in key_note_map:
        base_note = key_note_map[key_char]
        note_in_scale = base_note + scale * 12
        if 0 <= note_in_scale <= 127:
            return note_in_scale
    return None


# Envía un mensaje 'note_off' después de un tiempo
def send_note_off(note):
    msg_off = mido.Message('note_off', note=note, velocity=0)
    outport.send(msg_off)
    print(f"Nota apagada: {note}")


# Maneja las pulsaciones de teclas
def on_press(key):
    global current_scale
    try:
        key_char = key.char
        note = get_note_for_key(key_char, current_scale)
        if note is not None:
            msg_on = mido.Message('note_on', note=note, velocity=64)
            outport.send(msg_on)
            print(f"Nota enviada: {note}")
            # Envía 'note_off' después de 0.5 segundos
            threading.Timer(0.5, send_note_off, args=(note,)).start()
    except AttributeError:
        # Ignora teclas especiales
        pass


# Inicia el listener del teclado
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Mantiene el programa en ejecución
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
