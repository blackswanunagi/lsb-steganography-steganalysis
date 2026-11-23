"""Cache un message dans le LSB du canal rouge uniquement
(marqueur de fin : 1111111111111110).

Usage : python lsb_red_channel_encode.py <entree.png> <sortie.png> "<message>"
"""
import sys

from PIL import Image

if len(sys.argv) != 4:
    print('Usage: python lsb_red_channel_encode.py <entree.png> <sortie.png> "<message>"')
    sys.exit(1)

entree, sortie, message = sys.argv[1], sys.argv[2], sys.argv[3]

# 1. On prépare le message
message_bin = ''.join(format(ord(i), '08b') for i in message) + '1111111111111110'

# 2. On ouvre l'image
img = Image.open(entree).convert("RGB")
pixels = img.load()

if len(message_bin) > img.size[0] * img.size[1]:
    raise ValueError("Message trop long pour cette image")

# 3. On cache le message dans les pixels (bit de poids faible du rouge)
idx = 0
for y in range(img.size[1]):
    for x in range(img.size[0]):
        if idx < len(message_bin):
            r, g, b = pixels[x, y]
            r = (r & ~1) | int(message_bin[idx])
            idx += 1
            pixels[x, y] = (r, g, b)

# 4. On enregistre la nouvelle image (PNG : format sans perte)
img.save(sortie)
print(f"C'est fait ! Regarde le fichier {sortie}")
