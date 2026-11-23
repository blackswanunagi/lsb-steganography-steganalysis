import React, { useState } from 'react';
import { Upload, Download, AlertCircle } from 'lucide-react';

const SteganographyApp = () => {
    const [mode, setMode] = useState('encode');
    const [fileType, setFileType] = useState('image');
    const [file, setFile] = useState(null);
    const [originalUrl, setOriginalUrl] = useState(null);
    const [text, setText] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [lsbNoise, setLsbNoise] = useState(null);

    // --- SECTION ANALYSE INDÉPENDANTE ---
    const [analysisFile, setAnalysisFile] = useState(null);
    const [analysisUrl, setAnalysisUrl] = useState(null);
    const [analysisLSB, setAnalysisLSB] = useState(null);
    const [analysisError, setAnalysisError] = useState('');
    const [lsbDist, setLsbDist] = useState(null);

    // --- IMAGE LSB ENCODING ---
    const encodeImageLSB = async (imageFile, message) => {
        return new Promise((resolve, reject) => {
            const img = new window.Image();
            const reader = new FileReader();
            reader.onload = (e) => {
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const data = imageData.data;
                    const messageBits = textToBinary(message) + '1111111111111110';
                    const maxBits = canvas.width * canvas.height;

                    if (messageBits.length > maxBits) {
                        reject(new Error('Message trop long pour cette image'));
                        return;
                    }

                    let idx = 0;
                    for (let y = 0; y < canvas.height; y++) {
                        for (let x = 0; x < canvas.width; x++) {
                            if (idx < messageBits.length) {
                                const pixelIndex = (y * canvas.width + x) * 4;
                                const r = data[pixelIndex];
                                data[pixelIndex] = (r & ~1) | parseInt(messageBits[idx]);
                                idx++;
                            }
                        }
                    }
                    ctx.putImageData(imageData, 0, 0);
                    canvas.toBlob((blob) => resolve(blob), 'image/png');
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(imageFile);
        });
    };

    const decodeImageLSB = async (imageFile) => {
        return new Promise((resolve, reject) => {
            const img = new window.Image();
            const reader = new FileReader();
            reader.onload = (e) => {
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const data = imageData.data;

                    let binaryMessage = '';
                    for (let y = 0; y < canvas.height; y++) {
                        for (let x = 0; x < canvas.width; x++) {
                            const pixelIndex = (y * canvas.width + x) * 4;
                            const r = data[pixelIndex];
                            binaryMessage += (r & 1).toString();
                        }
                    }

                    const delimiterIndex = binaryMessage.indexOf('1111111111111110');
                    if (delimiterIndex !== -1) {
                        const messageBits = binaryMessage.substring(0, delimiterIndex);
                        resolve(binaryToText(messageBits));
                    } else {
                        reject(new Error('Aucun message caché trouvé ou délimiteur manquant'));
                    }
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(imageFile);
        });
    };

    // --- AUDIO LSB ENCODING ---
    const encodeAudioLSB = async (audioFile, message) => {
        const buffer = await audioFile.arrayBuffer();
        const view = new DataView(buffer);
        const dataOffset = 44;
        const messageBits = textToBinary(message + '###END###');

        if (messageBits.length > (buffer.byteLength - dataOffset) / 2) {
            throw new Error("Message trop long");
        }

        let bitIndex = 0;
        for (let i = dataOffset; i < buffer.byteLength && bitIndex < messageBits.length; i += 2) {
            let sample = view.getInt16(i, true);
            sample = (sample & 0xFFFE) | parseInt(messageBits[bitIndex++]);
            view.setInt16(i, sample, true);
        }

        return new Blob([buffer], { type: 'audio/wav' });
    };

    const decodeAudioLSB = async (audioFile) => {
        const buffer = await audioFile.arrayBuffer();
        const view = new DataView(buffer);
        const dataOffset = 44;
        let bits = '';
        let message = '';
        const endMarker = '###END###';

        for (let i = dataOffset; i < buffer.byteLength; i += 2) {
            bits += (view.getInt16(i, true) & 1);
            if (bits.length >= 8) {
                const byte = parseInt(bits.slice(0, 8), 2);
                bits = bits.slice(8);
                const char = String.fromCharCode(byte);
                message += char;
                if (message.endsWith(endMarker)) {
                    return message.slice(0, -endMarker.length);
                }
            }
        }
        return message;
    };

    // --- LSB NOISE DETECTION ---
    const detectImageNoise = async (imageFile) => {
        return new Promise((resolve) => {
            const img = new Image();
            const reader = new FileReader();
            reader.onload = (e) => {
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;

                    let changes = 0;
                    for (let i = 4; i < data.length; i += 4) {
                        if ((data[i] & 1) !== (data[i - 4] & 1)) {
                            changes++;
                        }
                    }
                    const ratio = changes / (data.length / 4);
                    resolve(ratio);
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(imageFile);
        });
    };

    const detectAudioNoise = async (audioFile) => {
        const buffer = await audioFile.arrayBuffer();
        const view = new DataView(buffer);
        const dataOffset = 44;
        let lsbCount = 0;
        let sampleCount = 0;

        for (let i = dataOffset; i < buffer.byteLength; i += 2) {
            const sample = view.getInt16(i, true);
            lsbCount += sample & 1;
            sampleCount++;
        }
        return lsbCount / sampleCount;
    };

    // --- EXTRACT LSB DATA FOR RGB CHANNELS ---
    const extractImageLSBData = async (file) => {
        return new Promise((resolve) => {
            const img = new Image();
            const reader = new FileReader();
            reader.onload = (e) => {
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;

                    const counts = {
                        Red: [0, 0],
                        Green: [0, 0],
                        Blue: [0, 0]
                    };

                    for (let i = 0; i < data.length; i += 4) {
                        for (let c = 0; c < 3; c++) {
                            if (data[i + c] & 1) {
                                counts[["Red", "Green", "Blue"][c]][1]++;
                            } else {
                                counts[["Red", "Green", "Blue"][c]][0]++;
                            }
                        }
                    }
                    resolve(counts);
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    };

    // --- INDEPENDENT ANALYSIS ---
    const runIndependentAnalysis = async () => {
        if (!analysisFile) {
            setAnalysisError('Veuillez sélectionner un fichier à analyser');
            return;
        }

        setAnalysisError('');

        try {
            if (analysisFile.type.startsWith('image')) {
                const lsbCounts = await extractImageLSBData(analysisFile);
                setLsbDist(lsbCounts);

                const ratios = Object.values(lsbCounts).map(([zero, one]) => one / (zero + one));
                setAnalysisLSB(Math.max(...ratios));

                const balanced = ratios.every(r => r >= 0.48 && r <= 0.52);
                setAnalysisError(
                    balanced
                        ? '✔ Distribution équilibrée sur tous les canaux (image probablement saine)'
                        : '❌ Déséquilibre détecté sur au moins un canal (suspicion de stéganographie LSB)'
                );
            } else {
                const ratio = await detectAudioNoise(analysisFile);
                setAnalysisLSB(ratio);
                setLsbDist(null);

                const balanced = ratio >= 0.40 && ratio <= 0.60;
                setAnalysisError(
                    balanced
                        ? '✔ Distribution LSB équilibrée (audio probablement sain)'
                        : '⚠️ Distribution LSB déséquilibrée (suspicion de stéganographie)'
                );
            }
        } catch (err) {
            setAnalysisError('Erreur lors de l\'analyse: ' + err.message);
        }
    };

    // --- LSB BAR CHART COMPONENT ---
    const LSBBarChartRGB = ({ data }) => {
        const ref = React.useRef();

        React.useEffect(() => {
            if (!data) return;

            const canvas = ref.current;
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const channels = ["Red", "Green", "Blue"];
            const colors = ['#f87171', '#34d399', '#60a5fa'];

            channels.forEach((channel, i) => {
                const [zero, one] = data[channel];
                const total = zero + one;
                const xOffset = 60 + i * 130;
                const max = Math.max(zero, one);

                // Draw bars
                ctx.fillStyle = colors[i];
                ctx.fillRect(xOffset, 180 - (zero / max) * 150, 40, (zero / max) * 150);
                ctx.fillRect(xOffset + 50, 180 - (one / max) * 150, 40, (one / max) * 150);

                // Labels
                ctx.fillStyle = '#000';
                ctx.font = '12px sans-serif';
                ctx.fillText(channel, xOffset + 10, 200);
                ctx.fillText('0s', xOffset + 5, 220);
                ctx.fillText('1s', xOffset + 55, 220);
                ctx.fillText(`${((one / total) * 100).toFixed(1)}%`, xOffset + 35, 165);
            });
        }, [data]);

        return (
            <div className="mt-6">
                <h4 className="font-semibold text-gray-700 mb-2">Distribution des LSB par canal</h4>
                <canvas ref={ref} width={450} height={230} className="border border-gray-300 rounded" />
            </div>
        );
    };

    // --- UTILS ---
    const textToBinary = (text) => text.split('').map(c => c.charCodeAt(0).toString(2).padStart(8, '0')).join('');

    const binaryToText = (binary) => {
        let text = '';
        for (let i = 0; i < binary.length; i += 8) {
            const byte = binary.substr(i, 8);
            const code = parseInt(byte, 2);
            if (code === 0) break;
            text += String.fromCharCode(code);
        }
        return text;
    };

    // --- HANDLERS ---
    const handleFileChange = (e) => {
        const f = e.target.files[0];
        if (f) {
            setFile(f);
            setOriginalUrl(URL.createObjectURL(f));
            setError('');
            setResult(null);
            setLsbNoise(null);
        }
    };

    const handleProcess = async () => {
        if (!file) return setError('Veuillez sélectionner un fichier');
        if (mode === 'encode' && !text.trim()) return setError('Veuillez entrer un message à cacher');

        setLoading(true);
        setError('');
        setResult(null);

        try {
            if (mode === 'encode') {
                const blob = fileType === 'image'
                    ? await encodeImageLSB(file, text)
                    : await encodeAudioLSB(file, text);
                setResult({ type: 'file', url: URL.createObjectURL(blob), blob });
            } else {
                const decoded = fileType === 'image'
                    ? await decodeImageLSB(file)
                    : await decodeAudioLSB(file);
                setResult({ type: 'text', text: decoded });
            }
        } catch (err) {
            setError(err.message || 'Une erreur est survenue');
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = () => {
        if (result?.type === 'file') {
            const a = document.createElement('a');
            a.href = result.url;
            a.download = `stego_${fileType === 'image' ? 'image.png' : 'audio.wav'}`;
            a.click();
        }
    };

    const handleDetectNoise = async () => {
        if (!file) return setError('Veuillez sélectionner un fichier');
        setError('');

        const ratio = fileType === 'image'
            ? await detectImageNoise(file)
            : await detectAudioNoise(file);
        setLsbNoise(ratio);
    };

    const handleAnalysisFileChange = (e) => {
        const f = e.target.files[0];
        if (!f) return;
        setAnalysisFile(f);
        setAnalysisUrl(URL.createObjectURL(f));
        setAnalysisLSB(null);
        setAnalysisError('');
        setLsbDist(null);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
            <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl p-8">
                <h1 className="text-4xl font-bold text-center mb-2 text-indigo-700">
                    🔐 Stéganographie LSB
                </h1>
                <p className="text-center text-gray-600 mb-8">
                    Cachez ou extrayez des messages dans des images PNG ou fichiers audio
                </p>

                {/* Mode */}
                <div className="mb-6 flex gap-4">
                    <button
                        onClick={() => setMode('encode')}
                        className={`flex-1 py-3 px-6 rounded-lg font-semibold transition ${
                            mode === 'encode' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                    >
                        🔒 Encoder
                    </button>
                    <button
                        onClick={() => setMode('decode')}
                        className={`flex-1 py-3 px-6 rounded-lg font-semibold transition ${
                            mode === 'decode' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                    >
                        🔓 Décoder
                    </button>
                </div>

                {/* Type */}
                <div className="mb-6 flex gap-4">
                    <button
                        onClick={() => setFileType('image')}
                        className={`flex-1 py-3 px-6 rounded-lg font-semibold transition ${
                            fileType === 'image' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                    >
                        🖼️ Image PNG
                    </button>
                    <button
                        onClick={() => setFileType('audio')}
                        className={`flex-1 py-3 px-6 rounded-lg font-semibold transition ${
                            fileType === 'audio' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                    >
                        🎵 Audio WAV
                    </button>
                </div>

                {/* Upload */}
                <div className="mb-6">
                    <input
                        type="file"
                        accept={fileType === 'image' ? 'image/png' : 'audio/wav'}
                        onChange={handleFileChange}
                        className="hidden"
                        id="fileInput"
                    />
                    <label
                        htmlFor="fileInput"
                        className="cursor-pointer block p-6 text-center border-2 border-dashed border-indigo-400 rounded-lg hover:bg-indigo-50 transition"
                    >
                        <Upload className="mx-auto mb-2 text-indigo-400" size={40} />
                        <p className="text-gray-700">
                            {file ? file.name : `Cliquez pour sélectionner un fichier ${fileType === 'image' ? 'PNG' : 'WAV'}`}
                        </p>
                    </label>
                </div>

                {/* Text input */}
                {mode === 'encode' && (
                    <div className="mb-6">
                        <label className="block font-semibold text-gray-700 mb-2">Message à cacher</label>
                        <textarea
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                            placeholder="Entrez votre message secret..."
                            className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                            rows={5}
                        />
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
                        <AlertCircle className="text-red-500 mr-2 flex-shrink-0" size={20} />
                        <span className="text-red-700">{error}</span>
                    </div>
                )}

                {/* Process buttons */}
                <div className="flex gap-4 mb-6">
                    <button
                        onClick={handleProcess}
                        disabled={loading}
                        className="flex-1 py-4 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400 transition"
                    >
                        {loading ? '⏳ Traitement...' : mode === 'encode' ? '🔒 Cacher le message' : '🔓 Extraire le message'}
                    </button>

                </div>

                {/* Noise indicator */}
                {lsbNoise !== null && (
                    <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <p className="font-semibold">Ratio de LSB à 1 : {(lsbNoise * 100).toFixed(2)}%</p>
                        <p className="mt-2">
                            {lsbNoise >= 0.48 && lsbNoise <= 0.52
                                ? '✔ Distribution équilibrée - Aucun message caché évident détecté'
                                : '⚠️ Distribution déséquilibrée - Possibilité de message caché détectée'}
                        </p>
                    </div>
                )}

                {/* Preview */}
                {file && originalUrl && (
                    <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                        <h4 className="font-semibold text-gray-700 mb-2">Fichier original :</h4>
                        {fileType === 'image' ? (
                            <img src={originalUrl} alt="Original" className="max-w-full rounded-lg" />
                        ) : (
                            <audio controls src={originalUrl} className="w-full" />
                        )}
                    </div>
                )}

                {/* Result */}
                {result && (
                    <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-lg">
                        <h3 className="text-lg font-semibold text-green-800 mb-4">
                            {mode === 'encode' ? '✓ Message caché avec succès' : '✓ Message extrait avec succès'}
                        </h3>
                        {result.type === 'file' ? (
                            <>
                                <div className="mb-4">
                                    <h4 className="font-semibold text-gray-700 mb-2">Résultat :</h4>
                                    {fileType === 'image' ? (
                                        <img src={result.url} alt="Stego" className="max-w-full rounded-lg" />
                                    ) : (
                                        <audio controls src={result.url} className="w-full" />
                                    )}
                                </div>
                                <button
                                    onClick={handleDownload}
                                    className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                                >
                                    <Download size={20} />
                                    Télécharger
                                </button>
                            </>
                        ) : (
                            <div className="bg-white p-4 rounded border border-green-300">
                                <p className="font-semibold text-gray-700 mb-2">Message décodé :</p>
                                <p className="text-gray-800 whitespace-pre-wrap">{result.text}</p>
                            </div>
                        )}
                    </div>
                )}

                {/* ================= ANALYSE INDÉPENDANTE ================= */}
                <div className="mt-12 p-8 bg-slate-50 border-2 border-dashed border-indigo-300 rounded-2xl">
                    <h2 className="text-2xl font-bold mb-2 text-indigo-700">
                        🔍 Analyse indépendante de stéganographie
                    </h2>
                    <p className="text-gray-600 mb-6">
                        Importez un fichier pour détecter la présence potentielle de stéganographie sans encoder ni décoder de message.
                    </p>

                    {/* Upload */}
                    <div className="mb-6">
                        <input
                            type="file"
                            accept="image/*,audio/wav"
                            onChange={handleAnalysisFileChange}
                            className="hidden"
                            id="analysisInput"
                        />
                        <label
                            htmlFor="analysisInput"
                            className="cursor-pointer block p-6 text-center border-2 border-dashed border-indigo-400 rounded-lg hover:bg-indigo-50 transition"
                        >
                            <Upload className="mx-auto mb-2 text-indigo-400" size={40} />
                            <p className="text-gray-700">
                                {analysisFile ? analysisFile.name : 'Cliquez pour sélectionner un fichier'}
                            </p>
                        </label>
                    </div>

                    {/* Bouton */}
                    <button
                        onClick={runIndependentAnalysis}
                        className="w-full py-4 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
                    >
                        Lancer l'analyse
                    </button>

                    {/* Erreur/Message */}
                    {analysisError && (
                        <div className={`mt-4 p-3 rounded ${
                            analysisError.startsWith('✔') ? 'bg-green-50 border border-green-200 text-green-800' : 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                        }`}>
                            {analysisError}
                        </div>
                    )}

                    {/* Résultats */}
                    {analysisLSB !== null && (
                        <div className="mt-6 p-5 bg-white border border-indigo-200 rounded-lg">
                            <h3 className="font-bold mb-3">📊 Résultats de l'analyse</h3>
                            <p className="mb-2">🔹 Ratio LSB maximal : {(analysisLSB * 100).toFixed(2)}%</p>
                            {analysisFile?.type.startsWith('image') ? (
                                <p className="text-sm text-gray-600">Analyse par canal RGB effectuée</p>
                            ) : (
                                <p className="text-sm text-gray-600">Analyse des échantillons audio effectuée</p>
                            )}
                        </div>
                    )}

                    {/* Preview */}
                    {analysisUrl && analysisFile?.type.startsWith('image') && (
                        <div className="mt-6">
                            <h4 className="font-semibold text-gray-700 mb-2">Aperçu :</h4>
                            <img src={analysisUrl} alt="Analyse preview" className="max-w-full rounded-lg" />
                        </div>
                    )}

                    {/* Chart RGB */}
                    {lsbDist && <LSBBarChartRGB data={lsbDist} />}
                </div>

                <div className="mt-6 text-center text-gray-600 text-sm">
                    <p>Méthode LSB (Least Significant Bit) - Les données sont cachées dans les bits de poids faible</p>
                </div>
            </div>
        </div>
    );
};

export default SteganographyApp;