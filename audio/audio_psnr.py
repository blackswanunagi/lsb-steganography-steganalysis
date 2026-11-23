"""PSNR entre un audio original et un audio stéganographié (WAV 16 bits).

Usage : python audio_psnr.py <original.wav> <stego.wav>
"""
import math
import sys
import wave

import numpy as np


def read_samples(path):
    with wave.open(path, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
    # float64 : évite le dépassement de capacité d'int16 lors de la soustraction
    return np.frombuffer(frames, dtype=np.int16).astype(np.float64)


def compute_psnr(audio_orig, audio_steg):
    samples1, samples2 = read_samples(audio_orig), read_samples(audio_steg)
    if len(samples1) != len(samples2):
        raise ValueError("Les deux audios doivent avoir la même taille")
    mse = np.mean((samples1 - samples2) ** 2)
    if mse == 0:
        return float('inf')
    max_value = 32767
    return 10 * math.log10((max_value ** 2) / mse)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python audio_psnr.py <original.wav> <stego.wav>")
        sys.exit(1)
    print(f"PSNR = {compute_psnr(sys.argv[1], sys.argv[2]):.2f} dB")
