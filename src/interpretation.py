import mido
import fluidsynth

# Configura FluidSynth
fs = fluidsynth.Synth()
fs.start(driver='alsa')  # Usa 'pulseaudio' si tienes problemas con 'alsa'

# Carga el SoundFont
soundfont_path = '/home/pablo/Downloads/arachno-soundfont-10-sf2/Arachno SoundFont - Version 1.0.sf2'
sfid = fs.sfload(soundfont_path)
fs.program_select(0, sfid, 0, 46)  # Banco 0, Preset 46 suele ser el arpa

# Abre un puerto MIDI para escuchar las notas
inport = mido.open_input()  # Abre el primer puerto MIDI disponible

print("Escuchando notas MIDI. Presiona Ctrl+C para salir.")

try:
    for msg in inport:
        if msg.type == 'note_on' and msg.velocity > 0:
            fs.noteon(0, msg.note, msg.velocity)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            fs.noteoff(0, msg.note)
except KeyboardInterrupt:
    print("Saliendo...")

# Cierra FluidSynth
fs.delete()
