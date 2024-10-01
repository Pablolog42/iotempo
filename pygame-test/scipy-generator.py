import numpy as np
from scipy.io.wavfile import write

def generate_note_waveform(frequency, duration, volume=0.25):
    fs = 44100  # Frecuencia de muestreo
    t = np.linspace(0, duration, int(fs * duration), False)
    note = np.sin(2 * np.pi * frequency * t)
    # Escalar la señal a 16 bits y ajustar el volumen
    audio = volume * note * (2**15 - 1) / np.max(np.abs(note))
    audio = audio.astype(np.int16)
    return audio

# Frecuencias de las notas
frequencies = [261.63, 293.66, 329.63]  # Do, Re, Mi
note_names = ['Do', 'Re', 'Mi']

# Generar y guardar los archivos de sonido
for freq, name in zip(frequencies, note_names):
    waveform = generate_note_waveform(freq, duration=2.0)
    write(f'{name}.wav', 44100, waveform)
