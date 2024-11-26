import time

import spidev

spi = spidev.SpiDev()
spi.open(0, 0)  # SPI bus 0, chip select 0 (CS0)
spi.max_speed_hz = 1350000


def read_adc(channel):
    command = [1, (8 + channel) << 4, 0]
    result = spi.xfer2(command)
    value = ((result[1] & 3) << 8) | result[2]
    return value


while True:
    value = read_adc(0)  # Leer solo el canal 0
    print("Canal 0:", value)
    time.sleep(0.5)
