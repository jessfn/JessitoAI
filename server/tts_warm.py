"""Precalienta la caché de voz con todas las frases que Jessito puede decir (respuestas de la base de datos).
Uso: DATABASE_URL=... python tts_warm.py   (con el servicio tts_service.py encendido)
"""
import os, re, json, time, urllib.request
import psycopg2

SPLIT = re.compile(r'[^.!?¿¡]+[.!?]*|[.!?]+')
OPEN = ['Lo siento mucho.', 'Ay, qué difícil.', 'Te entiendo.', 'Estoy contigo.', 'Uy, eso suena duro.', 'Te escucho.', 'Aquí estoy.', 'Cuéntame.', 'Entiendo.', 'Qué bien.', 'Qué bonito.',
        'Me alegra.', 'Qué padre.', 'Genial.', 'Jeje.', 'Ay, qué lindo.', 'Me encanta.', 'Qué ternura.', 'Gracias, de verdad.', 'Wow.', 'Ay, qué sorpresa.', 'No lo puedo creer.', 'Mmm.',
        'A ver.', 'Déjame pensar.', 'Buena pregunta.', 'Ay, qué sueño.', 'Con calma.', 'Despacito.', 'Claro.', 'Va.', 'Listo.', 'Respira.']
EMO = {'sad': 'sad', 'listening': 'listening', 'happy': 'happy', 'love': 'love', 'surprised': 'surprised', 'thinking': 'thinking', 'sleepy': 'sleepy', 'neutral': 'happy', 'angry': 'angry'}

con = psycopg2.connect(os.environ['DATABASE_URL']); cur = con.cursor()
cur.execute("SELECT text,emotion FROM responses")
items = set()
for t, e in cur.fetchall():
    if '{' in t: continue
    for s in SPLIT.findall(t):
        s = re.sub(r'\bjessito\b', 'Yessito', s.strip(), flags=re.I)
        if s: items.add((s, 'happy' if e == 'neutral' else e))
for o in OPEN:
    for e in ('happy', 'sad', 'listening', 'love', 'surprised', 'thinking', 'sleepy'):
        items.add((o, e))
items = sorted(items)
print(f'{len(items)} frases por calentar', flush=True)
t0 = time.time(); miss = 0
for i, (s, e) in enumerate(items):
    req = urllib.request.Request('http://127.0.0.1:3071/tts', data=json.dumps({'text': s, 'emotion': e, 'voice': 'em_santa', 'mult': 1}).encode(), headers={'content-type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            r.read(); miss += r.headers.get('x-cache') == 'miss'
    except Exception as ex:
        print('fallo', s, ex, flush=True)
    if i % 50 == 0: print(f'{i}/{len(items)} ({time.time() - t0:.0f}s)', flush=True)
print(f'LISTO: {len(items)} frases, {miss} nuevas, {time.time() - t0:.0f}s', flush=True)
