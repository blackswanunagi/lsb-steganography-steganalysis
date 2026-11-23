"""Cache un message texte dans un fichier WAV 16 bits (LSB de chaque échantillon).

Format : les 32 premiers échantillons stockent la longueur du message (en bits),
les suivants stockent le message encodé en UTF-8.

Usage : python audio_hide.py <entree.wav> <sortie.wav> "<message>"
"""
import sys
import wave

import numpy as np


def text_to_bits(text):
    byte_array = text.encode('utf-8')
    bits = []
    for byte in byte_array:
        bits.extend([int(b) for b in bin(byte)[2:].rjust(8, '0')])
    return bits


def int_to_bits(value, bits_length=32):
    return [int(b) for b in bin(value)[2:].rjust(bits_length, '0')]


def hide_message(audio_in, audio_out, message):
    wav = wave.open(audio_in, mode='rb')
    frames = wav.readframes(wav.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16).copy()

    message_bits = text_to_bits(message)
    message_length = len(message_bits)

    length_bits = int_to_bits(message_length, 32)
    total_bits = 32 + message_length
    if total_bits > len(samples):
        raise ValueError("Message trop long pour cet audio")

    for i in range(32):
        samples[i] = (samples[i] & ~1) | length_bits[i]
    for i in range(message_length):
        samples[i + 32] = (samples[i + 32] & ~1) | message_bits[i]

    wav_out = wave.open(audio_out, mode='wb')
    wav_out.setparams(wav.getparams())
    wav_out.writeframes(samples.tobytes())

    wav.close()
    wav_out.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Usage: python audio_hide.py <entree.wav> <sortie.wav> "<message>"')
        sys.exit(1)
    hide_message(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"Message caché avec succès dans {sys.argv[2]}")
