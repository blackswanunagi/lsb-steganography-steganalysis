# LSB Steganography & Steganalysis

Hide and **extract** secret messages in **images** and **audio** with Least Significant Bit (LSB) steganography, **detect** them with statistical steganalysis, measure the distortion with **PSNR** — as Python command-line tools and a **React web app**.

> *FR — Stéganographie LSB (dissimulation et extraction de messages) dans des images et des fichiers audio, stéganalyse statistique, mesure de qualité (PSNR), en Python et via une application web React.*

## Repository layout

```
image/     Python tools for PNG images
audio/     Python tools for 16-bit WAV audio
web-app/   React + Vite + Tailwind app (everything runs in the browser)
samples/   sample message and steganalysis notes
```

## Image tools — [`image/`](image/)

| Script | Purpose |
|---|---|
| `encode_text_lsb.py` | Hide a text file in the LSB of every R, G, B value (null byte as end marker). |
| `lsb_red_channel_encode.py` | Hide a message in the red channel only (`1111111111111110` end marker). |
| `lsb_channel_scanner.py` | **Extract / scan**: read the LSBs of R, G, B and RGB and print the readable text found. |
| `lsb_image_analysis.py` | Steganalysis: LSB 0/1 distribution per channel, with histograms. |
| `image_psnr.py` | PSNR between cover and stego image. |

```bash
python image/encode_text_lsb.py cover.png samples/message.txt stego.png
python image/lsb_channel_scanner.py stego.png 60
python image/image_psnr.py cover.png stego.png
```

## Audio tools — [`audio/`](audio/)

| Script | Purpose |
|---|---|
| `generate_wav.py` | Generate a 5 s, 440 Hz test WAV (`audio_original.wav`). |
| `audio_hide.py` | Hide a message: message length on the first 32 samples, then the UTF-8 message, one bit per 16-bit sample. |
| `audio_extract.py` | **Extract** the message; with the original file, compare LSB statistics first to detect the embedding. |
| `audio_stego_interactive.py` | Interactive encode / decode with a `###END###` marker. |
| `make_test_files.py` | Build five test files (short, long, special characters, numbers). |
| `audio_psnr.py` | PSNR between original and stego audio. |
| `lsb_audio_analysis.py` | LSB distribution plots for WAV/MP3, mono or stereo. |

```bash
cd audio
python generate_wav.py
python audio_hide.py audio_original.wav stego.wav "Secret message"
python audio_extract.py audio_original.wav stego.wav   # detect + extract
python audio_psnr.py audio_original.wav stego.wav
```

## Web app — [`web-app/`](web-app/)

React 19 + Vite + Tailwind: encode and decode a message in an image, then analyse the LSB distribution per RGB channel with charts. No server, no upload: everything is processed locally with the Canvas API.

```bash
cd web-app && npm install && npm run dev
```

## Results (tested)

| Test | Result |
|---|---|
| Audio hide → extract (5 s WAV) | Message recovered exactly |
| Audio LSB ratio in the message zone | 0.487 original → 0.400 stego → flagged as suspicious |
| Audio PSNR | ≈ 123 dB — inaudible change |
| Image RGB / red-channel hide → scan | Message recovered from the right channel only |
| Image PSNR (random 160×120 cover) | ≈ 78 dB |

## How it works

- **Embedding:** each message bit replaces the least significant bit of a colour value (image) or of a 16-bit sample (audio): a change of ±1, invisible and inaudible.
- **Extraction:** read those bits back in the same order until the length prefix or end marker says to stop.
- **Detection:** embedding changes the 0/1 balance of the LSB plane where data was written; the scripts measure it and compare it with the original or with the expected distribution.
- **Quality:** PSNR (dB) measures how close the stego file is to the original — higher is better.

[`samples/steganalysis_notes.md`](samples/steganalysis_notes.md) summarises the steganalysis families (visual, statistical, structural, transform-domain, machine learning, blind vs targeted).

## Fixes made while publishing

- **PSNR (image and audio):** the subtraction was done on `uint8` / `int16`, which overflows and gives wrong results; arrays are now converted to `float64`.
- **Interactive audio encoder:** it modified the LSB of *every byte*, including the high byte of each 16-bit sample (an audible ±256 change); it now writes only to the low byte of each sample.
- **Image analysis:** the verdict announced for the red channel was computed on the blue channel.

## Limitations

- Detection is a simple statistical heuristic; stronger tests (chi-square attack, RS analysis, ML classifiers) are the next step.
- Messages are not encrypted before embedding; combining with AES would add confidentiality.
- LSB data does not survive lossy compression (JPEG, MP3): use PNG and WAV.

**Author:** Hiba El Hjouji — Cybersecurity engineering student, FST Guéliz (Université Cadi Ayyad).
