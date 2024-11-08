import mido
import random
from pynput import keyboard
import asyncio
import aiohttp

# Variables globales para almacenar los valores de la modulación
valor_modulacion_actual = None
valor_modulacion_anterior = None

# API para obtener el precio de Bitcoin en USD desde Binance
API_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

TIEMPO_ENTRE_LLAMADOS = 3

# Función para obtener el precio de Bitcoin desde la API de Binance
async def fetch_modulation_value():
    global valor_modulacion_actual, valor_modulacion_anterior
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(API_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Extraer el precio de Bitcoin en USD
                        precio_bitcoin = float(data['price'])

                        # Actualizar los valores de modulación
                        if valor_modulacion_actual is not None:
                            valor_modulacion_anterior = valor_modulacion_actual
                        valor_modulacion_actual = precio_bitcoin

                        print(f"Precio de Bitcoin (USD): {precio_bitcoin}")
                    else:
                        print("Error al obtener datos de la API")

            except Exception as e:
                print(f"Error en la consulta a la API: {e}")

            # Esperar segundos antes de la próxima consulta
            await asyncio.sleep(TIEMPO_ENTRE_LLAMADOS)


# Función para normalizar el valor entre 0 y 1
def normalize_value(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


# Función para obtener la señal modulada
def get_signal():
    global valor_modulacion_actual, valor_modulacion_anterior

    # Si no hay datos anteriores, retornar un valor aleatorio
    if valor_modulacion_actual is None or valor_modulacion_anterior is None:
        return random.random()

    # Calcular la diferencia entre los valores actuales y anteriores
    diferencia = abs(valor_modulacion_actual - valor_modulacion_anterior)

    # Normalizar la diferencia entre un rango típico de cambios
    return normalize_value(diferencia, 0, 50)


# Diccionario para mapear teclas a notas MIDI
key_to_note = {
    'd': 60,  # Do (C4)
    'r': 62,  # Re (C4)
    'm': 64,  # Mi (C4)
    'f': 65,  # Fa (C4)
    's': 67,  # Sol (C4)
    'l': 69,  # La (C4)
    't': 71,  # Si (C4)
}


# Función para ajustar la nota según la señal recibida, dividiendo en octavas
def adjust_note_octave(note):
    signal = get_signal()  # Obtiene el valor modulado
    print(f"Señal modulada: {signal:.2f}")

    # Asignar octavas según el rango de la señal (10 niveles)
    if 0.0 <= signal < 0.1:
        return max(note - 24, 0)  # Octava -2
    elif 0.1 <= signal < 0.2:
        return max(note - 12, 0)  # Octava -1
    elif 0.2 <= signal < 0.3:
        return note  # Octava base
    elif 0.3 <= signal < 0.4:
        return min(note + 12, 127)  # Octava +1
    elif 0.4 <= signal < 0.5:
        return min(note + 24, 127)  # Octava +2
    elif 0.5 <= signal < 0.6:
        return min(note + 36, 127)  # Octava +3
    elif 0.6 <= signal < 0.7:
        return min(note + 48, 127)  # Octava +4
    elif 0.7 <= signal < 0.8:
        return min(note + 60, 127)  # Octava +5
    elif 0.8 <= signal < 0.9:
        return min(note + 72, 127)  # Octava +6
    elif 0.9 <= signal <= 1.0:
        return min(note + 84, 127)  # Octava +7
    else:
        return note


# Función para enviar una nota MIDI
def send_midi_note_on(note):
    adjusted_note = adjust_note_octave(note)
    msg = mido.Message('note_on', note=adjusted_note, velocity=64)
    output.send(msg)


def send_midi_note_off(note):
    adjusted_note = adjust_note_octave(note)
    msg = mido.Message('note_off', note=adjusted_note, velocity=64)
    output.send(msg)


# Asincrónicamente captura las teclas presionadas
async def keyboard_listener():
    loop = asyncio.get_event_loop()
    with keyboard.Events() as events:
        while True:
            event = await loop.run_in_executor(None, events.get)
            if isinstance(event, keyboard.Events.Press):
                key = event.key
                try:
                    k = key.char
                    if k in key_to_note:
                        send_midi_note_on(key_to_note[k])
                    if k == 'q':
                        print("Saliendo...")
                        break
                except AttributeError:
                    pass
            elif isinstance(event, keyboard.Events.Release):
                try:
                    k = event.key.char
                    if k in key_to_note:
                        send_midi_note_off(key_to_note[k])
                except AttributeError:
                    pass


# Iniciar el loop asincrónico para obtener los datos de la API y el teclado
async def main():
    fetch_task = asyncio.create_task(fetch_modulation_value())
    keyboard_task = asyncio.create_task(keyboard_listener())
    await asyncio.gather(fetch_task, keyboard_task)


# Ejecutar el programa
output = mido.open_output(mido.get_output_names()[0])
asyncio.run(main())
