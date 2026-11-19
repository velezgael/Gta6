# Máquina de clips virales (VAIZITY)

Convierte un vídeo largo (directo, IRL, podcast, gameplay) en clips verticales 9:16 listos para TikTok, YouTube Shorts y Reels.

**Qué hace:**
1. **Transcribe** el audio con Whisper, en local. Funciona en español, inglés y mezcla de los dos.
2. **Busca los mejores momentos**: gritos y picos de volumen, un buen arranque en los primeros 3 segundos, palabras de reacción ("no mames", "bro", "let's go", "jajaja"…), exclamaciones y ritmo de habla.
3. **Corta** clips de 20 a 45 s, siempre empezando al principio de una frase y terminando al final de otra.
4. **Encuadra en vertical**. Si hay una cara, la sigue con recorte 9:16. Si no la hay (gameplay), pone el vídeo entero con el fondo difuminado.
5. **Subtítulos animados** palabra a palabra, en mayúsculas, con la palabra activa en amarillo, como en los clips virales.
6. Genera para cada clip **portada, título sugerido, hashtags y transcripción**.

## Uso

```bash
cd clipper
python3 clip.py "https://www.youtube.com/watch?v=..."   # pegar un enlace (YouTube, Twitch, Kick)
python3 clip.py "ENLACE" --tramo 01:00:00-01:30:00     # solo un tramo de un directo largo
python3 clip.py mi_directo.mp4                       # 5 clips automáticos
python3 clip.py mi_directo.mp4 -n 10 --lang es       # 10 clips, español
python3 clip.py mi_directo.mp4 --min 15 --max 30     # clips más cortos
python3 clip.py mi_directo.mp4 --layout blur         # gameplay: vídeo completo + fondo difuminado
python3 clip.py mi_directo.mp4 --hook                # texto gancho arriba los primeros 3 s
python3 clip.py mi_directo.mp4 --at 01:02:10-01:02:40   # cortar un momento concreto (repetible)
```

Los resultados quedan en `output/<nombre>/`:
- `clip_XX.mp4`: el clip vertical 1080x1920
- `clip_XX.jpg`: la portada
- `CLIPS.txt`: los títulos sugeridos, los hashtags y la transcripción de cada clip

## Instalación (una sola vez)

```bash
pip install yt-dlp sherpa-onnx soundfile numpy pillow "opencv-python-headless<5"
mkdir -p models && cd models
curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2 | tar xj
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx
curl -L -o yunet.onnx https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx
```

## Permisos

Usa solo vídeos tuyos o de creadores que te den permiso, por ejemplo a través de su programa oficial de clippers. Subir clips de otros sin permiso puede acabar en reclamaciones de copyright y en el cierre del canal.
