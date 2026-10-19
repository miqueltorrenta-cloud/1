# EZE – edición del vídeo (Remotion)

Edición del vídeo vertical 2160×3840 · 30 fps · 18,27 s con subtítulos en catalán,
microzooms y música de fondo original con ducking.

## Pasos

```bash
npm install
cp /ruta/al/video_ezeproject_comprimido.mp4 public/source.mp4

# 1. Transcripción en catalán con timestamps por palabra (Whisper large-v3)
#    Requiere acceso de red a huggingface.co para descargar el modelo.
pip install faster-whisper
python scripts/transcribe.py public/source.mp4 src/data/captions.json
#    -> revisar src/data/captions.json y corregir solo errores evidentes

# 2. (Opcional) regenerar música y curva de ducking
python scripts/make_music.py public/music_original.wav
python scripts/make_ducking.py public/source.mp4 src/data/ducking.json

# 3. Render final (máxima calidad: frames PNG, x264 CRF 12 preset slow, BT.709, AAC 320k)
REMOTION_BROWSER=/ruta/a/chrome-headless-shell npm run render
```

## Decisiones

- **Calidad**: misma resolución, fps y relación de aspecto; frames extraídos en PNG
  (`OffthreadVideo transparent`), captura PNG y x264 CRF 12. La voz original va a volumen 1, sin procesar.
- **Subtítulos** (`src/Captions.tsx`): Montserrat SemiBold 100 px, #FFFFFF, sombra negra suave,
  centrados, margen inferior 11,5 %, ancho máx. 72 % (libre de la barra derecha de TikTok/Reels), 2 líneas máx.
- **Zooms** (`src/zooms.ts`): colocados a mano por plano (cortes en 3,67 / 9,27 / 13,07 s),
  1,04–1,06× habituales y un único acento de 1,08× en el logo EZE, con easing suave.
- **Música** (`scripts/make_music.py`): base reggaetón/dembow 100 % original sintetizada
  (sin samples ni canciones de terceros, libre de derechos). 103,6 BPM, Fa menor, dos secciones
  con crossfade equal-power exactamente en el corte de 9,27 s.
- **Ducking** (`scripts/make_ducking.py`): música ~28 dB bajo la voz cuando se habla y
  ~22 dB bajo la voz en pausas, ataque rápido con look-ahead y release lento.
