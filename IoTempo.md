![[Pasted image 20240930143116.png]]

### Paso 0: Crear enviroment
Se crea venv

Activar venv:
```
source ~/iotempo-venv/bin/activate
```

Agregar activacion de venv a startup file
nano ~/.bashrc


Se instalan dependencias:
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install build-essential python3-dev libasound2-dev 
pip install wheel
pip install adafruit-ads1x15 adafruit-blinka adafruit-circuitpython-ads1x15 numpy scipy simpleaudio pygame
```

Habilitar I2C, serial y otras interfaces:
```
sudo raspi-config
```

-----
### **Configuración de la Salida de Audio**

Antes de empezar, necesitamos asegurarnos de que la Raspberry Pi está configurada para enviar el audio a través del jack de 3.5 mm.

#### **Paso 1: Configurar la Salida de Audio a través del Jack de 3.5 mm**

Ejecuta el siguiente comando en la terminal para forzar que el audio salga por el jack analógico:

`amixer cset numid=3 1`

### **Paso 2: Instalación de Dependencias**

Necesitaremos algunas librerías para generar y reproducir sonidos:

- **numpy**: Para manejar cálculos numéricos y generar las ondas de sonido.
- **simpleaudio**: Para reproducir los sonidos generados.

#### **Instalar las Librerías**

`pip3 install numpy simpleaudio`


### **Paso 3: Código Python**

A continuación, te presento el código completo que:

- Lee los valores del ADS1115.
- Detecta las interrupciones de los haces láser.
- Reproduce la nota correspondiente cuando se interrumpe un haz.

python

Copy code

```python
import time
import threading
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
import simpleaudio as sa

# Configuración del bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Crear objeto ADS1115
ads = ADS.ADS1115(i2c)

# Configurar el rango de ganancia
ads.gain = 1  # Rango de entrada ±4.096V

# Crear objetos de canales para los sensores y el potenciómetro
sensor_channels = [
    AnalogIn(ads, ADS.P0),  # Sensor 1
    AnalogIn(ads, ADS.P1),  # Sensor 2
    AnalogIn(ads, ADS.P2)   # Sensor 3
]

pot_channel = AnalogIn(ads, ADS.P3)  # Potenciómetro

# Nombres de las notas y frecuencias correspondientes a cada sensor
notes = ['Do', 'Re', 'Mi']
frequencies = [261.63, 293.66, 329.63]  # Frecuencias en Hz para Do, Re, Mi

# Estados anteriores de los sensores
previous_states = [False] * len(sensor_channels)

# Duración de la nota en segundos
note_duration = 1.0

# Función para reproducir una nota sin bloquear el bucle principal
def play_tone(frequency, duration):
    fs = 44100  # Frecuencia de muestreo
    t = np.linspace(0, duration, int(fs * duration), False)
    # Generar una onda senoidal
    note = np.sin(frequency * t * 2 * np.pi)
    # Ajustar el volumen al 25%
    volume = 0.25  # 25% del volumen máximo
    # Escalar la señal de audio
    audio = volume * note * (2**15 - 1) / np.max(np.abs(note))
    audio = audio.astype(np.int16)
    # Reproducir el audio sin bloquear
    sa.play_buffer(audio, 1, 2, fs)

# Función para iniciar la reproducción en un hilo separado
def play_tone_thread(frequency, duration):
    thread = threading.Thread(target=play_tone, args=(frequency, duration), daemon=True)
    thread.start()

try:
    print("Iniciando detección de interrupciones. Presiona Ctrl+C para salir.")
    while True:
        # Leer el valor del potenciómetro y ajustar el umbral
        pot_value = pot_channel.value
        # Escalar el valor del potenciómetro a un rango apropiado para el umbral
        min_threshold = 5000   # Umbral mínimo
        max_threshold = 30000  # Umbral máximo
        threshold = pot_value
        if threshold < min_threshold:
            threshold = min_threshold
        elif threshold > max_threshold:
            threshold = max_threshold

        # Opcional: Imprimir el umbral actual
        print(f"Umbral ajustado: {threshold}")

        for i, channel in enumerate(sensor_channels):
            sensor_value = channel.value
            # Imprimir los valores para depuración (opcional)
            # print(f"Sensor {i}: Valor={sensor_value}")

            # Detectar interrupción del haz láser
            if sensor_value < threshold and not previous_states[i]:
                print(f"--> {notes[i]} tocada (Sensor {i} activado)")
                play_tone_thread(frequencies[i], note_duration)
                previous_states[i] = True
            elif sensor_value >= threshold and previous_states[i]:
                print(f"    {notes[i]} liberada (Sensor {i} desactivado)")
                previous_states[i] = False

        # Esperar un breve periodo antes de la siguiente lectura
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Saliendo del programa.")

```

# Iteracion 2: Usando archivos wav y pygame:

Se crean los. wav:

```python
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

```

```python
import time
import threading
import pygame
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Inicializar pygame mixer
pygame.mixer.init()

# Duración de las notas en milisegundos
note_duration_ms = 500  # Puedes ajustar este valor

volume_level = float(input("Ingrese Volumen (entre 0-1): "))


# Cargar los sonidos de las notas
note_files = {'Do': 'Do.wav', 'Re': 'Re.wav', 'Mi': 'Mi.wav'}
note_sounds = {}
for note_name, file_name in note_files.items():
    note_sounds[note_name] = pygame.mixer.Sound(file_name)
    note_sounds[note_name].set_volume(volume_level)  # Ajustar el volumen al 25%

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

# Función para detener la nota después de la duración especificada
def stop_note_after_delay(note_name, delay_ms):
    time.sleep(delay_ms / 1000.0)
    note_sounds[note_name].stop()

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
                # Reproducir la nota
                note_sounds[note_name].play()
                # Iniciar un hilo para detener la nota después de la duración especificada
                threading.Thread(target=stop_note_after_delay, args=(note_name, note_duration_ms), daemon=True).start()
                previous_states[i] = True
            elif sensor_value <= threshold and previous_states[i]:
                # Actualizar el estado de la nota
                previous_states[i] = False

        time.sleep(0.05)  # Ajusta el tiempo según sea necesario

except KeyboardInterrupt:
    print("Saliendo del programa.")
finally:
    pygame.mixer.quit()

```

**NOTA: TEST 3 PYGAME ES EL QUE MEJOR FUNCIONA POR AHORA.**