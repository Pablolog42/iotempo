import asyncio

import aiohttp
import mido
import spidev

# Configuración SPI para el MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI bus 0, chip select 0
spi.max_speed_hz = 1350000

# Variables para modulación basada en Bitcoin
valor_modulacion_actual = None
valor_modulacion_anterior = None

# Configuración MIDI
midi_output = mido.open_output(mido.get_output_names()[0])  # Usa el primer puerto MIDI disponible

# Umbral para activar la nota MIDI
THRESHOLD = 950

# Estado de las notas para evitar repeticiones
notas_activas = [False] * 8

# API de Binance para obtener el precio de Bitcoin
API_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

# Diccionario que mapea canales ADC a notas MIDI
canal_a_nota = {
    0: 60,  # Do (C4)
    1: 62,  # Re (D4)
    2: 64,  # Mi (E4)
    3: 65,  # Fa (F4)
    4: 67,  # Sol (G4)
    5: 69,  # La (A4)
    6: 71,  # Si (B4)
    7: 72,  # Do (C5)
}


# Leer el valor de un canal específico del MCP3008
def read_adc(channel):
    command = [1, (8 + channel) << 4, 0]
    result = spi.xfer2(command)
    value = ((result[1] & 3) << 8) | result[2]
    return value


# Obtener la señal modulada basada en el precio de Bitcoin
def get_signal():
    global valor_modulacion_actual, valor_modulacion_anterior

    # Si no hay datos anteriores, retorna un valor por defecto
    if valor_modulacion_actual is None or valor_modulacion_anterior is None:
        return 0.5

    # Calcular la diferencia entre valores actual y anterior
    diferencia = abs(valor_modulacion_actual - valor_modulacion_anterior)

    # Normalizar la diferencia entre un rango típico (0-50)
    return min(max(diferencia / 50, 0), 1)


# Ajustar la octava de la nota según la señal
def adjust_note_octave(note):
    signal = get_signal()
    print(f"Señal modulada: {signal:.2f}")

    # Asignar octavas según la señal (0-1)
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


# Enviar una nota MIDI
def send_midi_note_on(note):
    adjusted_note = adjust_note_octave(note)
    msg = mido.Message('note_on', note=adjusted_note, velocity=64)
    midi_output.send(msg)


# Enviar el apagado de una nota MIDI
def send_midi_note_off(note):
    adjusted_note = adjust_note_octave(note)
    msg = mido.Message('note_off', note=adjusted_note, velocity=64)
    midi_output.send(msg)


# Leer continuamente los canales del ADC
async def adc_loop():
    while True:
        for channel in range(8):
            value = read_adc(channel)
            if value > THRESHOLD:
                if not notas_activas[channel]:
                    print(f"Canal {channel} activado con valor {value}")
                    send_midi_note_on(canal_a_nota[channel])
                    notas_activas[channel] = True
            else:
                if notas_activas[channel]:
                    print(f"Canal {channel} desactivado con valor {value}")
                    send_midi_note_off(canal_a_nota[channel])
                    notas_activas[channel] = False
        await asyncio.sleep(0.05)  # Evitar sobrecargar el SPI


# Obtener el precio de Bitcoin de la API de Binance
async def fetch_bitcoin_price():
    global valor_modulacion_actual, valor_modulacion_anterior
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(API_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        precio_bitcoin = float(data['price'])
                        if valor_modulacion_actual is not None:
                            valor_modulacion_anterior = valor_modulacion_actual
                        valor_modulacion_actual = precio_bitcoin
                        print(f"Precio de Bitcoin: {precio_bitcoin}")
                    else:
                        print("Error al obtener datos de la API.")
            except Exception as e:
                print(f"Error en la consulta de la API: {e}")
            await asyncio.sleep(5)  # Consulta cada 5 segundos


# Ejecutar ambas tareas asincrónicas
async def main():
    await asyncio.gather(adc_loop(), fetch_bitcoin_price())


# Ejecutar el programa
asyncio.run(main())
