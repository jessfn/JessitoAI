"""Convierte a MP3 todas las frases ya guardadas en la caché WAV.  Uso: TTS_MP3_DIR=... python tts_mp3_backfill.py"""
import os, glob, soundfile as sf
import tts_mp3
CACHE = os.environ.get('TTS_CACHE', '/var/cache/jessito-tts')
os.makedirs(tts_mp3.MP3_DIR, exist_ok=True)
keys = tts_mp3.read_manifest(); n = 0
for w in sorted(glob.glob(os.path.join(CACHE, '*.wav'))):
    k = os.path.basename(w)[:-4]
    if os.path.exists(os.path.join(tts_mp3.MP3_DIR, k + '.mp3')): keys.add(k); continue
    a, sr = sf.read(w, dtype='float32')
    data = tts_mp3.encode(a)
    with open(os.path.join(tts_mp3.MP3_DIR, k + '.mp3'), 'wb') as f: f.write(data)
    keys.add(k); n += 1
tts_mp3.write_manifest(keys)
print(f'MP3 listos: {len(keys)} ({n} nuevos)')
