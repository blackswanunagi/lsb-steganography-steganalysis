# Steganography Web App

React 19 + Vite + Tailwind CSS app to hide and extract text in images with LSB steganography, and to analyse an image's LSB distribution per RGB channel (charts with recharts).

Everything runs in the browser through the Canvas API: no file is uploaded anywhere.

```bash
npm install
npm run dev      # development server
npm run build    # production build in dist/
```

Main component: [`src/SteganographyApp.jsx`](src/SteganographyApp.jsx).
