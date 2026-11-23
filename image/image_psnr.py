"""PSNR entre une image originale et une image stéganographiée.

Usage : python image_psnr.py <originale.png> <stego.png>
"""
import math
import sys

import numpy as np
from PIL import Image


def calculer_psnr(image_originale, image_stego):
    # float64 : avec uint8, img1 - img2 "boucle" (ex. 0 - 1 = 255) et fausse le MSE
    img1 = np.asarray(Image.open(image_originale).convert("RGB"), dtype=np.float64)
    img2 = np.asarray(Image.open(image_stego).convert("RGB"), dtype=np.float64)
    if img1.shape != img2.shape:
        raise ValueError("Les deux images doivent avoir la même taille")
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * math.log10(255.0 / math.sqrt(mse))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python image_psnr.py <originale.png> <stego.png>")
        sys.exit(1)
    print(f"PSNR = {calculer_psnr(sys.argv[1], sys.argv[2]):.2f} dB")
