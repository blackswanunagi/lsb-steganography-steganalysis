import wave
import numpy as np
import struct

filename = "audio_original.wav"  # même nom, donc ça écrase l'ancien
duration = 5.0                   # durée réduite à 5 secondes
freq = 440.0                    # fréquence 440 Hz (La)
framerate = 44100               # fréquence d'échantillonnage
amplitude = 32767               # amplitude max (16 bits)

# Générer les échantillons pour une onde sinusoïdale
t = np.linspace(0, duration, int(framerate * duration), endpoint=False)
samples = (amplitude * np.sin(2 * np.pi * freq * t)).astype(np.int16)

with wave.open(filename, 'w') as wav_file:
    nchannels = 1
    sampwidth = 2  # 16 bits = 2 octets
    nframes = len(samples)
    comptype = "NONE"
    compname = "not compressed"

    wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

    for s in samples:
        wav_file.writeframes(struct.pack('<h', s))

print(f"Fichier '{filename}' créé : {duration} secondes d’onde sinusoïdale à {freq} Hz.")
