# LSB Steganography & Steganalysis

Python tools to **hide text in images** using Least Significant Bit (LSB) steganography, and to **detect** LSB embedding in images and audio through statistical analysis of bit distributions.

> *FR — Outils Python de stéganographie LSB (dissimulation de texte dans une image) et de stéganalyse statistique sur images et fichiers audio.*

## Tools

| Script | Purpose |
|---|---|
| [`encode_text_lsb.py`](encode_text_lsb.py) | Hides a text file in a PNG image by writing its bits into the LSB of each R, G, B value (null byte as end marker). |
| [`lsb_image_analysis.py`](lsb_image_analysis.py) | Steganalysis of an image: LSB 0/1 distribution per channel (first quarter of the image), plotted as histograms, with a verdict on the red channel. |
| [`lsb_audio_analysis.py`](lsb_audio_analysis.py) | Steganalysis of an audio file (WAV/MP3, mono or stereo): LSB distribution of the 16-bit samples over the first half of the file. |

## Usage

```bash
pip install -r requirements.txt

# Hide a message
python encode_text_lsb.py cover.png samples/message.txt stego.png

# Analyse an image / an audio file
python lsb_image_analysis.py stego.png
python lsb_audio_analysis.py suspect.wav
```

## How it works

- **Embedding:** each character becomes 8 bits; each bit replaces the least significant bit of one colour value. A change of ±1 on a 0–255 value is invisible to the eye. Capacity: `height × width × 3` bits.
- **Detection:** LSB embedding pushes the proportion of 0s and 1s in the LSB plane towards 50/50 in the region where data was written (the start of the image or file). The scripts measure that proportion and flag it when it falls in the suspicious range.

[`samples/steganalysis_notes.md`](samples/steganalysis_notes.md) summarises the main steganalysis families (visual, statistical, structural, transform-domain, machine learning, blind vs targeted).

## Limitations

- The detection is a **simple statistical heuristic**: natural images and audio can also have balanced LSBs, so it gives false positives. Stronger tests (chi-square attack, RS analysis, ML classifiers) are the next step.
- No extraction script yet: the decoder (reading LSBs back until the null byte) is planned.
- Messages are not encrypted before embedding.

## Author

**Hiba El Hjouji** — Cybersecurity engineering student, FST Guéliz (Université Cadi Ayyad).
