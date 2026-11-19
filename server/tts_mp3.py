"""Guarda cada frase de voz también como MP3 estático (/voz/<clave>.mp3) para que el navegador la guarde y suene al instante."""
import os, json, threading
import numpy as np, lameenc

MP3_DIR = os.environ.get('TTS_MP3_DIR', '')
_lock = threading.Lock()

def encode(a):
    pcm = (np.clip(np.asarray(a, dtype=np.float32), -1, 1) * 32767).astype('<i2').tobytes()
    e = lameenc.Encoder(); e.set_bit_rate(40); e.set_in_sample_rate(24000); e.set_channels(1); e.set_quality(3)
    return bytes(e.encode(pcm)) + bytes(e.flush())

def write_manifest(keys):
    p = os.path.join(MP3_DIR, 'index.json')
    with open(p + '.tmp', 'w') as f: json.dump(sorted(keys), f)
    os.replace(p + '.tmp', p)

def read_manifest():
    try: return set(json.load(open(os.path.join(MP3_DIR, 'index.json'))))
    except Exception: return set()

def save(key, a):
    if not MP3_DIR: return
    os.makedirs(MP3_DIR, exist_ok=True)
    data = encode(a)
    p = os.path.join(MP3_DIR, key + '.mp3')
    with open(p + '.tmp', 'wb') as f: f.write(data)
    os.replace(p + '.tmp', p)
    with _lock:
        ks = read_manifest(); ks.add(key); write_manifest(ks)
