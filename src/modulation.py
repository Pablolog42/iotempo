import mido
from pynput import keyboard
import time

# Lista de puertos MIDI disponibles
available_ports = mido.get_output_names()
if not available_ports:
    raise OSError("No se encontró ningún puerto MIDI disponible. Asegúrate de que el puerto MIDI virtual esté configurado.")

# Abrir el primer puerto MIDI disponible
output = mido.open_output(available_ports[0])

# Diccionario para mapear teclas a notas MIDI
key_to_note = {
    'd': 60,  # Do (C4)
    'r': 62,  # Re (D4)
    'm': 64,  # Mi (E4)
    'f': 65,  # Fa (F4)
    's': 67,  # Sol (G4)
    'l': 69,  # La (A4)
    't': 71,  # Si (B4)
}

# Función para enviar una nota MIDI
def send_midi_note_on(note):
    msg = mido.Message('note_on', note=note, velocity=64)
    output.send(msg)
    print(f"Note-on enviada: {note}")

def send_midi_note_off(note):
    msg = mido.Message('note_off', note=note, velocity=64)
    output.send(msg)
    print(f"Note-off enviada: {note}")


# Función que se ejecuta cuando se presiona una tecla
def on_press(key):
    try:
        k = key.char  # Obtiene la tecla presionada si es alfanumérica
        if k in key_to_note:
            send_midi_note_on(key_to_note[k])
    except AttributeError:
        pass  # Ignorar teclas especiales que no tienen atributo 'char'

# Función que se ejecuta cuando se suelta una tecla
def on_release(key):
    try:
        k = key.char  # Obtiene la tecla soltada si es alfanumérica
        if k in key_to_note:
            send_midi_note_off(key_to_note[k])
        # Para salir, presiona 'q'
        if k == 'q':
            return False
    except AttributeError:
        pass  # Ignorar teclas especiales que no tienen atributo 'char'

# Listener para detectar las teclas presionadas
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("Presiona 'q' para salir.")
    listener.join()

# Cerrar el puerto MIDI al final
output.close()
