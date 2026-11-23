"""Extraction / scan LSB d'une image : lit les LSB des canaux R, G, B et RGB
et affiche le texte lisible trouvé au début de l'image.

Fonctionne avec encode_text_lsb.py (canal RGB) et lsb_red_channel_encode.py (canal R).

Usage : python lsb_channel_scanner.py <image.png> [nb_caracteres]
"""
import sys

from PIL import Image


def extraire_canal(pixels, largeur, hauteur, mode, nb_caracteres):
    nb_bits = nb_caracteres * 8
    bits = []
    for y in range(hauteur):
        for x in range(largeur):
            r, g, b = pixels[x, y][:3]
            if mode == 'R':
                bits.append(r & 1)
            elif mode == 'G':
                bits.append(g & 1)
            elif mode == 'B':
                bits.append(b & 1)
            else:  # RGB
                bits.extend((r & 1, g & 1, b & 1))
            if len(bits) >= nb_bits:
                break
        if len(bits) >= nb_bits:
            break

    message = ""
    for i in range(0, len(bits) - 7, 8):
        valeur = int(''.join(str(b) for b in bits[i:i + 8]), 2)
        if valeur == 0:  # marqueur de fin de encode_text_lsb.py
            break
        # Caractères lisibles uniquement, un point pour les autres
        message += chr(valeur) if 32 <= valeur <= 126 else "."
    return message


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Usage: python lsb_channel_scanner.py <image.png> [nb_caracteres]")
        sys.exit(1)
    nb = int(sys.argv[2]) if len(sys.argv) == 3 else 50
    img = Image.open(sys.argv[1]).convert("RGB")
    px = img.load()
    w, h = img.size
    print("--- SCAN DES CANAUX LSB ---")
    for canal in ['R', 'G', 'B', 'RGB']:
        print(f"Canal {canal:<3} : {extraire_canal(px, w, h, canal, nb)}")
