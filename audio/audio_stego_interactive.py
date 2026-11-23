"""Stéganographie audio LSB interactive (encodage / décodage avec marqueur de fin).

Le message est suivi de ###END### ; le décodage lit les LSB jusqu'au marqueur.
Seul l'octet de poids faible de chaque échantillon est modifié (pas de bruit audible).
"""
import wave

END_MARKER = "###END###"


def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)


def encode_audio_lsb(input_wav, output_wav, message):
    bits = text_to_bits(message + END_MARKER)

    with wave.open(input_wav, 'rb') as wav:
        params = wav.getparams()
        step = wav.getsampwidth()  # 2 pour du 16 bits : 1 bit par échantillon
        frames = bytearray(wav.readframes(wav.getnframes()))

    if len(bits) > len(frames) // step:
        raise ValueError("Message trop long pour cet audio")

    for i, bit in enumerate(bits):
        pos = i * step  # octet de poids faible (little-endian)
        frames[pos] = (frames[pos] & 0b11111110) | int(bit)

    with wave.open(output_wav, 'wb') as out:
        out.setparams(params)
        out.writeframes(frames)

    print("Message caché avec succès")


def decode_audio_lsb(stego_wav):
    with wave.open(stego_wav, 'rb') as wav:
        step = wav.getsampwidth()
        frames = wav.readframes(wav.getnframes())

    bits = ""
    message = ""
    for byte in frames[::step]:
        bits += str(byte & 1)
        if len(bits) == 8:
            message += chr(int(bits, 2))
            bits = ""
            if message.endswith(END_MARKER):
                return message[:-len(END_MARKER)]
    return ""


if __name__ == "__main__":
    print("=== Stéganographie Audio LSB ===")
    print("1. Encoder un message")
    print("2. Décoder un message")
    choix = input("Choix (1/2) : ").strip()

    if choix == "1":
        encode_audio_lsb(input("Fichier WAV original : ").strip(),
                         input("Fichier WAV de sortie : ").strip(),
                         input("Message secret : ").strip())
    elif choix == "2":
        message = decode_audio_lsb(input("Fichier WAV stéganographié : ").strip())
        print("Message extrait :", message if message else "(aucun message trouvé)")
    else:
        print("Choix invalide")
