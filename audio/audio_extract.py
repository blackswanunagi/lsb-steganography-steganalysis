"""Steganalyse et extraction d'un message caché par audio_hide.py.

1. Compare la proportion de LSB à 1 entre l'audio original et l'audio suspect
   sur la zone du message.
2. Si la différence dépasse un seuil, extrait le message (longueur sur 32 bits,
   puis le message UTF-8).

Usage :
  python audio_extract.py <stego.wav>                    # extraction seule
  python audio_extract.py <original.wav> <stego.wav>     # analyse + extraction
"""
import sys
import wave

import numpy as np

THRESHOLD = 0.01


def bits_to_text(bits):
    bytes_list = []
    for b in range(0, len(bits), 8):
        byte = bits[b:b + 8]
        bytes_list.append(int(''.join(str(bit) for bit in byte), 2))
    return bytes(bytes_list).decode('utf-8', errors='ignore')


def bits_to_int(bits):
    return int(''.join(str(b) for b in bits), 2)


def read_samples(audio_file):
    with wave.open(audio_file, mode='rb') as wav:
        frames = wav.readframes(wav.getnframes())
    return np.frombuffer(frames, dtype=np.int16)


def lsb_ones_ratio(samples, n_bits):
    return float(np.sum(samples[:n_bits] & 1)) / n_bits


def extract_message(audio_file):
    samples = read_samples(audio_file)
    message_length = bits_to_int([samples[i] & 1 for i in range(32)])
    if message_length <= 0 or 32 + message_length > len(samples):
        return ""
    message_bits = [samples[i + 32] & 1 for i in range(message_length)]
    return bits_to_text(message_bits)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print("Message extrait :", extract_message(sys.argv[1]))
    elif len(sys.argv) == 3:
        original, stego = read_samples(sys.argv[1]), read_samples(sys.argv[2])
        zone = bits_to_int([stego[i] & 1 for i in range(32)]) + 32
        zone = max(64, min(zone, len(stego), len(original)))
        p_orig, p_steg = lsb_ones_ratio(original, zone), lsb_ones_ratio(stego, zone)
        print(f"Proportion de LSB à 1 (original, zone message) : {p_orig:.3f}")
        print(f"Proportion de LSB à 1 (suspect,  zone message) : {p_steg:.3f}")
        if abs(p_steg - p_orig) > THRESHOLD:
            print("Le fichier semble contenir un message caché.")
            print("Message extrait :", extract_message(sys.argv[2]))
        else:
            print("Aucune modification suspecte détectée dans la zone analysée.")
    else:
        print(__doc__)
        sys.exit(1)
