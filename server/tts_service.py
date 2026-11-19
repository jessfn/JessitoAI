"""Servicio de voz de Jessito: Kokoro (red neuronal abierta de texto a voz) en español, voz masculina "Santa".
Escucha solo en 127.0.0.1:3071; la API de Node lo expone como /api/tts.  Guarda en disco cada frase ya generada.
"""
import os, sys, json, hashlib, threading, re
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import numpy as np, soundfile as sf, torch
from kokoro import KPipeline

torch.set_num_threads(int(os.environ.get('TTS_THREADS', '3')))
PORT = int(os.environ.get('TTS_PORT', '3071'))
CACHE = os.environ.get('TTS_CACHE', '/var/cache/jessito-tts')
os.makedirs(CACHE, exist_ok=True)
VOICES = {'em_santa', 'em_alex', 'ef_dora'}
SPEED = {'sad': .9, 'sleepy': .85, 'happy': 1.0, 'surprised': 1.05, 'angry': 1.05, 'love': .95, 'thinking': .95, 'listening': 1.0, 'neutral': 1.0}
PIPE = KPipeline(lang_code='e')
LOCK = threading.Lock()
RSS_LIMIT = int(os.environ.get('TTS_RSS_MB', '2800'))

def rss_mb():
    try:
        for l in open('/proc/self/status'):
            if l.startswith('VmRSS'): return int(l.split()[1]) // 1024
    except Exception: pass
    return 0

def synth(text, voice, speed):
    key = hashlib.sha1(f'{voice}|{speed:.2f}|{text}'.encode()).hexdigest()
    path = os.path.join(CACHE, key + '.wav')
    if os.path.exists(path):
        return open(path, 'rb').read(), True
    if not LOCK.acquire(timeout=25):
        raise TimeoutError('ocupado')
    try:
        if os.path.exists(path):
            return open(path, 'rb').read(), True
        chunks = [np.asarray(a) for _, _, a in PIPE(text, voice=voice, speed=speed)]
        a = np.concatenate(chunks) if chunks else np.zeros(2400, dtype=np.float32)
        tmp = path + '.tmp'
        sf.write(tmp, a, 24000, subtype='PCM_16', format='WAV')
        os.replace(tmp, path)
    finally:
        LOCK.release()
    return open(path, 'rb').read(), False

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body, ctype='application/json'):
        self.send_response(code); self.send_header('content-type', ctype); self.send_header('content-length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        self._send(200, b'{"ok":true}') if self.path == '/health' else self._send(404, b'{}')
    def do_POST(self):
        if self.path != '/tts': return self._send(404, b'{}')
        try:
            n = int(self.headers.get('content-length', 0))
            if n > 4000: return self._send(413, b'{}')
            b = json.loads(self.rfile.read(n) or b'{}')
            text = re.sub(r'\s+', ' ', str(b.get('text', ''))).strip()[:280]
            if not text: return self._send(400, b'{"error":"vacio"}')
            voice = b.get('voice') if b.get('voice') in VOICES else 'em_santa'
            mult = min(1.3, max(.75, float(b.get('mult') or 1)))
            speed = round(min(1.3, max(.7, SPEED.get(str(b.get('emotion')), 1.0) * mult)) * 20) / 20
            wav, hit = synth(text, voice, speed)
            self.send_response(200); self.send_header('content-type', 'audio/wav'); self.send_header('content-length', str(len(wav)))
            self.send_header('x-cache', 'hit' if hit else 'miss'); self.end_headers(); self.wfile.write(wav)
            if not hit and rss_mb() > RSS_LIMIT:                    # PyTorch va acumulando memoria: se reinicia solo (systemd lo vuelve a levantar)
                print(f'reinicio por memoria ({rss_mb()} MB)', flush=True)
                threading.Timer(0.4, lambda: os._exit(0)).start()
        except TimeoutError:
            self._send(503, b'{"error":"ocupado"}')
        except Exception as e:
            print('error', e, file=sys.stderr, flush=True); self._send(500, b'{"error":"tts"}')

if __name__ == '__main__':
    synth('Hola, soy Yessito.', 'em_santa', 1.0)        # calienta el modelo
    print(f'tts listo en {PORT}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
