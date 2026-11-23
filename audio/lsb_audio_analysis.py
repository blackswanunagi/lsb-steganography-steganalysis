import sys
import numpy as np
import matplotlib.pyplot as plt
import librosa

def lsb_audio_distribution(audio_path):
    # Charger audio (mono ou stéréo)
    y, sr = librosa.load(audio_path, sr=None, mono=False)
    
    # Gestion mono/stéréo
    if y.ndim == 1:
        channels = {"Mono": y}
    else:
        channels = {"Left": y[0], "Right": y[1]}

    plt.figure(figsize=(8, 4))
    print(f"Audio : {audio_path}")
    print("\n--- Analyse par canal (première moitié des échantillons) ---")

    ratios = []

    for i, (name, data) in enumerate(channels.items(), 1):
        # Prendre seulement la première moitié
        half_data = data[:len(data)//2]

        # Convertir float [-1,1] en int16
        samples = (half_data * 32767).astype(np.int16)
        lsb = samples & 1
        zeros = np.sum(lsb == 0)
        ones = np.sum(lsb == 1)
        total = zeros + ones
        ratio = ones / total
        ratios.append(ratio)

        perc_zeros = zeros / total * 100
        perc_ones = ones / total * 100

        print(f"{name} → 0s: {zeros} ({perc_zeros:.2f}%) | 1s: {ones} ({perc_ones:.2f}%) | Ratio 1s: {ratio:.4f}")

        plt.subplot(1, len(channels), i)
        plt.bar(['0', '1'], [perc_zeros, perc_ones], color=['blue', 'green'])
        plt.ylim(0, 100)
        plt.ylabel("Pourcentage (%)")
        plt.title(f"{name} LSB (1/2 audio)")

    # Interprétation uniquement pour le premier canal
    first_ratio = ratios[0]
    print("\n--- Interprétation ---")
    if 0.49 <= first_ratio <= 0.51:
        print(f"❌ {list(channels.keys())[0]} LSB déséquilibré (suspicion de stéganographie LSB)")
    else:
        print(f"✔ {list(channels.keys())[0]} LSB équilibré (audio probablement sain)")

    plt.suptitle("Distribution LSB par canal audio (1/2 échantillons)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lsb_audio_analysis.py <audio_file>")
        sys.exit(1)

    lsb_audio_distribution(sys.argv[1])
