# Steganography Web App

🌐 **Live: https://blackswanunagi.github.io/lsb-steganography-steganalysis/**

React 19 + Vite + Tailwind CSS app to hide and extract text in **PNG images and WAV audio files** with LSB steganography, and to run an independent steganalysis of a file (LSB distribution charts).

Everything runs in the browser: no file is uploaded anywhere.

```bash
npm install
npm run dev      # development server
npm run build    # production build in dist/
```

Main component: [`src/SteganographyApp.jsx`](src/SteganographyApp.jsx). Deployed to GitHub Pages on every push to `main` that changes `web-app/`.
