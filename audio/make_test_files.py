"""
Script pour créer plusieurs fichiers audio de test avec différents messages
"""
import wave
import numpy as np


def text_to_bits(text):
    """Convertit du texte en liste de bits"""
    byte_array = text.encode('utf-8')
    bits = []
    for byte in byte_array:
        bits.extend([int(b) for b in bin(byte)[2:].rjust(8, '0')])
    return bits


def int_to_bits(value, bits_length=32):
    """Convertit un entier en liste de bits"""
    return [int(b) for b in bin(value)[2:].rjust(bits_length, '0')]


def hide_message(audio_in, audio_out, message):
    """Cache un message dans un fichier audio"""
    try:
        wav = wave.open(audio_in, mode='rb')
        frames = wav.readframes(wav.getnframes())
        samples = np.frombuffer(frames, dtype=np.int16).copy()

        message_bits = text_to_bits(message)
        message_length = len(message_bits)

        length_bits = int_to_bits(message_length, 32)
        total_bits = 32 + message_length
        
        if total_bits > len(samples):
            print(f"❌ Message trop long pour {audio_out}")
            wav.close()
            return False

        # Cacher la longueur
        for i in range(32):
            samples[i] = (samples[i] & ~1) | length_bits[i]
        
        # Cacher le message
        for i in range(message_length):
            samples[i + 32] = (samples[i + 32] & ~1) | message_bits[i]

        # Sauvegarder
        wav_out = wave.open(audio_out, mode='wb')
        wav_out.setparams(wav.getparams())
        wav_out.writeframes(samples.tobytes())

        wav.close()
        wav_out.close()
        
        print(f"✅ {audio_out} créé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


# ====================================================================
# TESTS AVEC DIFFÉRENTS MESSAGES
# ====================================================================

print("="*70)
print("CRÉATION DE FICHIERS AUDIO DE TEST")
print("="*70)

# Vérifier que audio_original.wav existe
import os
if not os.path.exists("audio_original.wav"):
    print("\n❌ ERREUR: audio_original.wav n'existe pas!")
    print("   Placez un fichier audio_original.wav dans le dossier.")
    exit(1)

print("\n📝 Création de 5 fichiers audio de test...\n")

# Test 1: Message court
hide_message(
    "audio_original.wav",
    "test1_court.wav",
    "Hello World!"
)

# Test 2: Message moyen
hide_message(
    "audio_original.wav",
    "test2_moyen.wav",
    "La cryptographie est fascinante. Elle permet de sécuriser les communications."
)

# Test 3: Message long
hide_message(
    "audio_original.wav",
    "test3_long.wav",
    "Ce projet de stéganographie audio utilise la méthode LSB pour cacher des messages "
    "secrets dans des fichiers WAV. La modification est imperceptible à l'oreille humaine "
    "car seul le bit de poids faible de chaque échantillon est modifié. Cette technique "
    "offre une excellente qualité audio tout en permettant de transmettre des informations "
    "confidentielles de manière discrète."
)

# Test 4: Message avec caractères spéciaux
hide_message(
    "audio_original.wav",
    "test4_special.wav",
    "Message avec émoticônes: 🔒🔐 et symboles: @#$%&*!? ñáéíóú"
)

# Test 5: Message numérique
hide_message(
    "audio_original.wav",
    "test5_nombres.wav",
    "Code secret: 123456789 - Coordonnées GPS: 33.5731° N, 7.5898° W"
)

print("\n" + "="*70)
print("TESTS CRÉÉS AVEC SUCCÈS!")
print("="*70)
print("\n📋 Fichiers créés:")
print("  • test1_court.wav      - Message court")
print("  • test2_moyen.wav      - Message moyen")
print("  • test3_long.wav       - Message long")
print("  • test4_special.wav    - Caractères spéciaux")
print("  • test5_nombres.wav    - Nombres et coordonnées")
print("\n💡 Pour tester l'extraction, utilisez:")
print("   python audio_extract.py test1_court.wav")
print("   python audio_extract.py audio_original.wav test2_moyen.wav")
print("   etc...\n")