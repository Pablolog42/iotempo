import time
import pygame
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

MAX_VOL = float(input("Ingrese volumen máximo (Entre 0-1): "))


# Inicializar pygame mixer
pygame.mixer.init()

# Cargar los sonidos de las notas
note_files = {'Do': 'Do.wav', 'Re': 'Re.wav', 'Mi': 'Mi.wav'}
note_sounds = {}
for note_name, file_name in note_files.items():
    note_sounds[note_name] = pygame.mixer.Sound(file_name)
    note_sounds[note_name].set_volume(MAX_VOL)  # Ajustar el volumen al 25%

# Configuración del bus I2C y ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1

# Configuración de los canales
sensor_channels = [
    AnalogIn(ads, ADS.P0),  # Sensor 1
    AnalogIn(ads, ADS.P1),  # Sensor 2
    AnalogIn(ads, ADS.P2)   # Sensor 3
]
pot_channel = AnalogIn(ads, ADS.P3)  # Potenciómetro

# Nombres de las notas correspondientes
notes = ['Do', 'Re', 'Mi']

# Estados de las notas
previous_states = [False] * len(sensor_channels)

# Umbral inicial (se ajustará con el potenciómetro)
threshold = 20000

try:
    print("Iniciando detección de interrupciones. Presiona Ctrl+C para salir.")
    while True:
        # Leer el valor del potenciómetro y ajustar el umbral
        pot_value = pot_channel.value
        min_threshold = 5000
        max_threshold = 30000
        threshold = pot_value
        if threshold < min_threshold:
            threshold = min_threshold
        elif threshold > max_threshold:
            threshold = max_threshold

        # Comentado para desactivar la impresión del umbral
        # print(f"Umbral ajustado: {threshold}")

        for i, channel in enumerate(sensor_channels):
            sensor_value = channel.value
            # Imprimir los valores para depuración (opcional)
            # print(f"Sensor {i}: Valor={sensor_value}")

            # Detectar interrupción del haz láser
            if sensor_value > threshold and not previous_states[i]:
                note_name = notes[i]
                print(f"--> {note_name} tocada (Sensor {i} activado)")
                # Reproducir la nota en loop infinito
                note_sounds[note_name].play(loops=-1)
                previous_states[i] = True
            elif sensor_value <= threshold and previous_states[i]:
                note_name = notes[i]
                print(f"    {note_name} liberada (Sensor {i} desactivado)")
                # Detener la nota
                note_sounds[note_name].stop()
                previous_states[i] = False

        time.sleep(0.05)  # Ajusta el tiempo según sea necesario

except KeyboardInterrupt:
    print("Saliendo del programa.")
finally:
    pygame.mixer.quit()
