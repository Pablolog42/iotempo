import mido
import keyboard
import time

# Configurar el puerto de salida MIDI virtual
output = mido.open_output('Virtual Port')

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

def send_midi_note_off(note):
    msg = mido.Message('note_off', note=note, velocity=64)
    output.send(msg)

# Loop principal para detectar teclas
print("Presiona 'q' para salir.")
try:
    while True:
        for key, note in key_to_note.items():
            if keyboard.is_pressed(key):
                send_midi_note_on(note)
                time.sleep(0.1)  # Esperar un poco para evitar repetir la nota
                send_midi_note_off(note)

        # Para salir, presiona 'q'
        if keyboard.is_pressed('q'):
            print("Saliendo...")
            break

finally:
    output.close()
