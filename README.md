# VAIZITY: canal de YouTube sobre GTA 6

Diez vídeos listos para subir, con guion, voz, animaciones, música original, montaje, miniatura, subtítulos y ficha de subida.

## Qué hay en cada carpeta `videos/NN-.../`

| Archivo | Para qué |
|---|---|
| `video.mp4` | Vídeo final 1080p 30 fps, audio a -14 LUFS (el estándar de YouTube) |
| `miniatura.jpg` | Miniatura de 1280x720 |
| `SUBIR.txt` | Título, descripción con capítulos, hashtags, etiquetas y ajustes. Se copia y se pega |
| `subtitulos.srt` | Subtítulos en español. Se suben en YouTube Studio → Subtítulos |
| `guion.txt` | Guion con marcas de tiempo |

En `canal/` están el banner (2560x1440) y el avatar (800x800).

## Investigación: qué está buscando la gente (18 nov 2026, un día antes del lanzamiento)

Lo más buscado sobre GTA 6 y el vídeo que responde a cada búsqueda:

1. **"¿A qué hora sale GTA 6?"**: el pico de búsquedas es hoy y mañana. Vídeo 01
2. **"GTA 6 precio / Ultimate"**: vídeo 02
3. **"GTA 6 PC"**: es la duda más repetida en foros. Vídeo 03
4. **"GTA 6 cuánto pesa / espacio"**: el juego ocupa unos 212 GB. Vídeo 04
5. **"Mapa GTA 6"**: vídeo 05
6. **"Personajes GTA 6 / Jason y Lucía"**: vídeo 06
7. **"Vice City"**: búsquedas por nostalgia. Vídeo 07
8. **"GTA 6 Online"**: vídeo 08
9. **"Consejos GTA 6"**: crecerá mucho después del lanzamiento. Vídeo 09
10. **"Historia, retrasos y filtración"**: vídeo 10

## Orden de publicación recomendado

| Cuándo | Vídeo | Por qué |
|---|---|---|
| **HOY, 18 nov** | 01 ¿A qué hora sale? | Caduca en 24 h. Súbelo ya |
| HOY, 18 nov | 04 Cuánto pesa | La gente está precargando ahora mismo |
| HOY, 18 nov | 02 Precio | Última compra antes del lanzamiento |
| 19 nov | 10 Historia (13 años) | El día del lanzamiento ("GTA 6 ya está aquí") |
| 19 nov | 09 Consejos | Para quien empieza a jugar |
| 20 nov | 06 Personajes | |
| 21 nov | 05 Mapa | |
| 22 nov | 03 PC | |
| 23 nov | 08 Online | |
| 24 nov | 07 Vice City | Contenido atemporal |

## Antes de subir

- **Verifica las cifras del vídeo 02 (precios) y del 04 (212 GB).** Salen de tiendas y medios, no de una página oficial que haya podido comprobar. Si Rockstar anuncia algo nuevo (PC, Online), los vídeos 03 y 08 necesitan una actualización.
- El vídeo 01 dice "medianoche, hora local", según el soporte de Rockstar citado por Forbes. Puede haber excepciones por tienda o región.
- Todas las imágenes son ilustraciones originales: no hay arte, logos ni metraje de Rockstar. La música está generada por código. Así no hay reclamaciones de Content ID.
- Marca "Contenido alterado o sintético" en YouTube Studio, porque la voz es sintética (TTS).

## Regenerar o crear vídeos nuevos

Los guiones están en `tools/content.py`. Añade un vídeo a la lista y ejecuta:

```bash
pip install piper-tts soundfile scipy numpy pillow
# voz es_ES-davefx-medium (no está incluida en el repo por su tamaño):
curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-es_ES-davefx-medium.tar.bz2 | tar xj
cp vits-piper-es_ES-davefx-medium/es_ES-davefx-medium.onnx* assets/voice/
cd tools && python3 build.py 11      # o: python3 build.py all
```

Las plantillas visuales disponibles son `title`, `stat`, `clock`, `bullets`, `text`, `compare`, `timeline`, `map`, `char` y `outro`.

Canal de fans, no afiliado a Rockstar Games ni a Take-Two Interactive.
