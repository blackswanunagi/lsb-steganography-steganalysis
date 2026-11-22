import sys
from PIL import Image
import numpy as np

def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text) + '00000000'  # marqueur fin

def encode_text_in_image(image_path, text_path, output_path):
    # Charger image
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img)
    h, w, _ = pixels.shape

    # Lire texte
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    bits = text_to_bits(text)
    max_bits = h * w * 3

    if len(bits) > max_bits:
        raise ValueError("❌ Texte trop long pour cette image")

    bit_idx = 0

    for y in range(h):
        for x in range(w):
            for c in range(3):  # R, G, B
                if bit_idx < len(bits):
                    pixels[y, x, c] = (pixels[y, x, c] & 254) | int(bits[bit_idx])
                    bit_idx += 1

    encoded_img = Image.fromarray(pixels)
    encoded_img.save(output_path)

    print("✔ Texte encodé avec succès")
    print(f"Image générée : {output_path}")
    print(f"Bits encodés : {len(bits)}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python encode_text_lsb.py <input.png> <text.txt> <output.png>")
        sys.exit(1)

    encode_text_in_image(sys.argv[1], sys.argv[2], sys.argv[3])
