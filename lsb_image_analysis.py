import sys
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def lsb_image_distribution(image_path):
    # Charger image RGB
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img)

    # Garder seulement le premier quart vertical
    quarter_pixels = pixels[:pixels.shape[0]//4, :, :]

    channels = {
        "Red": quarter_pixels[:, :, 0],
        "Green": quarter_pixels[:, :, 1],
        "Blue": quarter_pixels[:, :, 2]
    }

    plt.figure(figsize=(9, 4))
    print(f"Image : {image_path}")
    print("\n--- Analyse par canal (1/4 des pixels) ---")

    ratios = []

    for i, (name, data) in enumerate(channels.items(), 1):
        lsb = data & 1
        zeros = np.sum(lsb == 0)
        ones = np.sum(lsb == 1)
        total = zeros + ones
        ratio = ones / total
        ratios.append(ratio)

        perc_zeros = zeros / total * 100
        perc_ones = ones / total * 100

        print(f"{name} → 0s: {zeros} ({perc_zeros:.2f}%) | 1s: {ones} ({perc_ones:.2f}%) | Ratio 1s: {ratio:.4f}")

        plt.subplot(1, 3, i)
        plt.bar(['0', '1'], [perc_zeros, perc_ones], color=['blue', 'green'])
        plt.ylim(0, 100)
        plt.ylabel("Pourcentage (%)")
        plt.title(f"{name} LSB (1/4)")

    # Interprétation uniquement pour Red
    print("\n--- Interprétation ---")
    red_zeros = 1 - ratios[0]  # proportion de 0 dans le canal Rouge
    if 0.48 <= red_zeros <= 0.60:
        print("❌ Red LSB déséquilibré (suspicion de stéganographie LSB)")
    else:
        print("✔ Red LSB équilibré (probablement sain)")

    plt.suptitle("Distribution LSB par canal (1/4 des pixels)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lsb_image_analysis.py <image.png>")
        sys.exit(1)

    lsb_image_distribution(sys.argv[1])
