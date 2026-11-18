"""Red neuronal propia de Blu, escrita desde cero con NumPy (sin frameworks, sin APIs).

  texto -> rasgos hash (palabras, bigramas, n-gramas de letras) -> bolsa de embeddings (D)
        -> capa oculta tanh (H) -> softmax sobre intenciones

Los datos salen de PostgreSQL (DATABASE_URL) o, sin base de datos, de seed_data.py.
Exporta pesos (model/weights.bin) y metadatos (model/model.json) que el navegador
carga y ejecuta con brain.js.  Uso:  python brain.py [--out ../public/model] [--epochs 60]
"""
import os, sys, re, json, time, math, random, argparse, unicodedata
import numpy as np

B, D, H = 8192, int(os.environ.get('BLU_D', 96)), int(os.environ.get('BLU_H', 160))          # buckets hash, dimension embedding, neuronas ocultas


# ---------- rasgos (debe ser IDENTICO a public/brain.js) ----------
def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def fnv(s):
    h = 2166136261
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h

def feature_counts(text):
    n = norm(text)
    toks = n.split(' ') if n else []
    f = []
    for i, w in enumerate(toks):
        f.append('w:' + w)
        if i + 1 < len(toks):
            f.append('b:' + w + '_' + toks[i + 1])
        p = '<' + w + '>'
        for k in (3, 4, 5):
            for j in range(len(p) - k + 1):
                f.append('c:' + p[j:j + k])
    c = {}
    for x in f:
        k = fnv(x) % B
        c[k] = c.get(k, 0) + 1
    return c


# ---------- aumento de datos ----------
PRE = ['', '', '', 'oye ', 'blu ', 'mira ', 'pues ', 'o sea ', 'a ver ', 'oye blu ', 'eh ', 'bueno ', 'sabes ', 'este ']
SUF = ['', '', '', ' blu', ' por favor', ' porfa', ' eh', ' jeje', ' amigo', ' pues', ' no', ' oye']
SYL = ['ka', 'zu', 'pi', 'to', 'mo', 'xe', 'ri', 'la', 'ne', 'vo', 'qui', 'ju', 'fa', 'gu', 'bra', 'plo', 'tz', 'sh', 'ñu', 'ky']

def typo(t, rng):
    if len(t) < 4:
        return t
    i = rng.randrange(1, len(t) - 1)
    m = rng.random()
    if m < .34:
        return t[:i] + t[i + 1:]                    # letra perdida
    if m < .67:
        return t[:i] + t[i + 1] + t[i] + t[i + 2:]  if i + 2 <= len(t) else t  # letras cambiadas
    return t[:i] + t[i] + t[i:]                     # letra repetida

SYN = {'muy': ['super', 'bien', 'demasiado', 'tan'], 'super': ['muy', 'bien'], 'estoy': ['ando', 'me siento', 'hoy estoy'], 'ando': ['estoy'],
       'quiero': ['necesito', 'me gustaria', 'tengo ganas de'], 'dime': ['cuentame', 'platicame'], 'cuentame': ['dime', 'platicame'],
       'hola': ['hey', 'buenas', 'que onda'], 'gracias': ['muchas gracias', 'mil gracias'], 'amigo': ['blu', 'compa'], 'mucho': ['bastante', 'un monton'],
       'tengo': ['siento', 'ando con'], 'puedes': ['podrias', 'sabes'], 'eres': ['estas', 'te ves'], 'adios': ['chao', 'bye'], 'bonito': ['lindo', 'chulo'],
       'lindo': ['bonito', 'tierno'], 'por favor': ['porfa', 'si puedes'], 'ahorita': ['ahora', 'en este momento'], 'hoy': ['el dia de hoy', 'ahorita']}

def augment(t, rng):
    w = t.split()
    for i, x in enumerate(w):
        if x.lower() in SYN and rng.random() < .25:
            w[i] = rng.choice(SYN[x.lower()])
    if len(w) > 3 and rng.random() < .2:
        del w[rng.randrange(len(w))]
    t = ' '.join(w)
    if rng.random() < .55: t = rng.choice(PRE) + t
    if rng.random() < .4:  t = t + rng.choice(SUF)
    if rng.random() < .25: t = typo(t, rng)
    if rng.random() < .15: t = t.upper()
    return t

def gibberish(rng):
    m = rng.random()
    if m < .4:  return ''.join(rng.choice(SYL) for _ in range(rng.randint(1, 4)))
    if m < .7:  return ''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(3, 10)))
    if m < .85: return ' '.join(''.join(rng.choice(SYL) for _ in range(rng.randint(1, 2))) for _ in range(rng.randint(2, 4)))
    return ''.join(rng.choice('0123456789') for _ in range(rng.randint(2, 6)))


# ---------- datos ----------
def load_data():
    url = os.environ.get('DATABASE_URL')
    if url:
        import psycopg2
        con = psycopg2.connect(url)
        cur = con.cursor()
        cur.execute("SELECT id,tag,emotion FROM intents ORDER BY id")
        intents = [dict(id=r[0], tag=r[1], emotion=r[2], users=[], replies=[]) for r in cur.fetchall()]
        by = {x['id']: x for x in intents}
        # lo que enseña una persona (source=user) tiene prioridad; ninguna frase puede estar en dos intenciones
        cur.execute("SELECT intent_id,text FROM utterances ORDER BY (source='user') DESC, id")
        seen = set()
        for iid, t in cur.fetchall():
            k = norm(t)
            if k and k not in seen:
                seen.add(k); by[iid]['users'].append(t)
        cur.execute("SELECT intent_id,text,emotion FROM responses")
        for iid, t, e in cur.fetchall():
            by[iid]['replies'].append((t, e))
        if os.environ.get('LEARN_LOGS', '1') == '1':
            tags = {x['tag']: x for x in intents}
            cur.execute("""SELECT user_text,intent FROM conversations
                           WHERE confidence>=0.93 AND intent IS NOT NULL AND intent<>'no_entiendo'
                             AND length(user_text) BETWEEN 3 AND 90 ORDER BY id DESC LIMIT 8000""")
            taken = {}
            for t, tag in cur.fetchall():
                k = norm(t)
                if tag in tags and k and k not in seen and taken.get(tag, 0) < 150:
                    seen.add(k); tags[tag]['users'].append(t); taken[tag] = taken.get(tag, 0) + 1
            if taken: print(f'aprendiendo de conversaciones reales: {sum(taken.values())} frases')
        con.close()
        return intents, 'postgres'
    from seed_data import I
    return [dict(id=i, tag=t, emotion=d['emotion'], users=list(d['users']),
                 replies=[(r, d['emotion']) for r in d['replies']]) for i, (t, d) in enumerate(I.items())], 'seed'


# ---------- modelo ----------
class Net:
    def __init__(self, ni, rng):
        self.E = (rng.standard_normal((B, D)) * .1).astype(np.float32)
        self.W1 = (rng.standard_normal((D, H)) * math.sqrt(1 / D)).astype(np.float32)
        self.b1 = np.zeros(H, np.float32)
        self.W2 = (rng.standard_normal((H, ni)) * math.sqrt(1 / H)).astype(np.float32)
        self.b2 = np.zeros(ni, np.float32)
        self.params = ['E', 'W1', 'b1', 'W2', 'b2']
        self.m = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        self.v = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        self.t = 0
        self.drop = float(os.environ.get('BLU_DROP', .12))

    def batch_csr(self, counts_list, drop, rng):
        rows, cols, vals = [], [], []
        for r, c in enumerate(counts_list):
            items = list(c.items())
            if drop > 0 and len(items) > 1:
                keep = [x for x in items if rng.random() > drop] or [items[0]]
                items = keep
            tot = math.sqrt(sum(v for _, v in items)) or 1.0
            for k, v in items:
                rows.append(r); cols.append(k); vals.append(v / tot)
        return np.array(rows), np.array(cols), np.array(vals, np.float32)

    def forward(self, counts_list, drop=0.0, rng=None):
        rows, cols, vals = self.batch_csr(counts_list, drop, rng)
        X = np.zeros((len(counts_list), B), np.float32)
        if len(rows):
            X[rows, cols] = vals
        h0 = X @ self.E
        h1 = np.tanh(h0 @ self.W1 + self.b1)
        logits = h1 @ self.W2 + self.b2
        z = logits - logits.max(1, keepdims=True)
        p = np.exp(z); p /= p.sum(1, keepdims=True)
        return p, (X, h0, h1)

    def step(self, counts_list, y, lr, rng):
        p, (X, h0, h1) = self.forward(counts_list, self.drop, rng)
        n = len(y)
        loss = -np.log(p[np.arange(n), y] + 1e-9).mean()
        dl = p.copy(); dl[np.arange(n), y] -= 1; dl /= n
        g = {'W2': h1.T @ dl, 'b2': dl.sum(0)}
        dh1 = (dl @ self.W2.T) * (1 - h1 * h1)
        g['W1'] = h0.T @ dh1; g['b1'] = dh1.sum(0)
        dh0 = dh1 @ self.W1.T
        g['E'] = X.T @ dh0
        self.t += 1
        for k in self.params:
            gk = g[k]
            self.m[k] = .9 * self.m[k] + .1 * gk
            self.v[k] = .999 * self.v[k] + .001 * gk * gk
            mh = self.m[k] / (1 - .9 ** self.t); vh = self.v[k] / (1 - .999 ** self.t)
            getattr(self, k).__isub__((lr * mh / (np.sqrt(vh) + 1e-8)).astype(np.float32))
        return loss

    def predict(self, texts):
        p, _ = self.forward([feature_counts(t) for t in texts])
        return p


def build_set(intents, tags, rng, per, with_gib=True, holdout=None):
    X, Y = [], []
    for yi, it in enumerate(intents):
        for u in it['users']:
            if holdout is not None and u in holdout:
                continue
            X.append(u); Y.append(yi)
            for _ in range(per):
                X.append(augment(u, rng)); Y.append(yi)
    if with_gib:
        gi = tags.index('no_entiendo')
        for _ in range(400):
            X.append(gibberish(rng)); Y.append(gi)
    return X, Y


def train(net, X, Y, epochs, rng, log=print, bs=96, lr0=4e-3):
    feats = [feature_counts(t) for t in X]
    idx = np.arange(len(X))
    for ep in range(epochs):
        rng.shuffle(idx)
        lr = lr0 * (0.5 * (1 + math.cos(math.pi * ep / epochs)) * .95 + .05)
        tot = 0; nb = 0
        for s in range(0, len(idx), bs):
            b = idx[s:s + bs]
            tot += net.step([feats[i] for i in b], np.array([Y[i] for i in b]), lr, rng); nb += 1
        if ep % 10 == 0 or ep == epochs - 1:
            log(f'  epoca {ep + 1:3d}/{epochs}  perdida {tot / nb:.4f}')


def accuracy(net, texts, labels):
    if not texts: return 0.0
    p = net.predict(texts)
    return float((p.argmax(1) == np.array(labels)).mean())


def export(net, intents, out, meta):
    os.makedirs(out, exist_ok=True)
    arrs = [net.E, net.W1, net.b1, net.W2, net.b2]
    blob = b''.join(a.astype('<f4').tobytes() for a in arrs)
    tmp = os.path.join(out, 'weights.bin.tmp')
    open(tmp, 'wb').write(blob); os.replace(tmp, os.path.join(out, 'weights.bin'))
    model = dict(B=B, D=D, H=H, NI=len(intents), pools={p['tag']: [dict(t=t, e=e) for t, e in p['replies']] for p in meta.get('pools', [])}, version=meta['version'], threshold=0.5,
                 trained_at=meta['trained_at'], n_examples=meta['n_examples'], val_acc=meta['val_acc'],
                 intents=[dict(tag=i['tag'], emotion=i['emotion'],
                               replies=[dict(t=t, e=e) for t, e in i['replies']]) for i in intents])
    tmp = os.path.join(out, 'model.json.tmp')
    json.dump(model, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
    os.replace(tmp, os.path.join(out, 'model.json'))
    # versión global (la usa el servidor para avisar a las apps abiertas)
    vp = os.path.join(os.path.dirname(os.path.abspath(out)), 'version.json')
    cur = {}
    try: cur = json.load(open(vp))
    except Exception: pass
    cur['model'] = meta['version']; cur.setdefault('app', 'dev'); cur['version'] = f"{cur['app']}.{cur['model']}"
    json.dump(cur, open(vp + '.tmp', 'w')); os.replace(vp + '.tmp', vp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'model'))
    ap.add_argument('--epochs', type=int, default=25)
    ap.add_argument('--per', type=int, default=16, help='variantes aumentadas por frase')
    ap.add_argument('--seed', type=int, default=7)
    a = ap.parse_args()
    t0 = time.time()
    rng = random.Random(a.seed); nrng = np.random.default_rng(a.seed)
    intents, src = load_data()
    pools = [i for i in intents if not i['users'] and i['replies']]
    intents = [i for i in intents if i['users'] and i['replies']]
    tags = [i['tag'] for i in intents]
    assert 'no_entiendo' in tags, 'falta la intencion no_entiendo'
    print(f'datos: {src} | intenciones={len(intents)} frases={sum(len(i["users"]) for i in intents)}')

    # 1) validación: se aparta ~15% de las frases base para medir si generaliza
    hold = set(); vx, vy = [], []
    for yi, it in enumerate(intents):
        if len(it['users']) >= 8:
            for u in rng.sample(it['users'], max(1, len(it['users']) // 7)):
                hold.add(u); vx.append(u); vy.append(yi)
    X, Y = build_set(intents, tags, rng, a.per, holdout=hold)
    net = Net(len(intents), nrng)
    print(f'entrenando (validación): {len(X)} ejemplos')
    train(net, X, Y, a.epochs, nrng)
    val = accuracy(net, vx, vy)
    print(f'precision en frases NUNCA vistas: {val * 100:.1f}% ({len(vx)} frases)')

    # 2) modelo final con todos los datos
    X, Y = build_set(intents, tags, rng, a.per)
    net = Net(len(intents), nrng)
    print(f'entrenando (final): {len(X)} ejemplos')
    train(net, X, Y, a.epochs, nrng)
    tr = accuracy(net, [x for x in X[:4000]], Y[:4000])
    ver = time.strftime('%Y%m%d%H%M%S')
    export(net, intents, a.out, dict(pools=pools, version=ver, trained_at=time.strftime('%Y-%m-%d %H:%M:%S'),
                                     n_examples=len(X), val_acc=round(val, 4)))
    print(f'listo en {time.time() - t0:.0f}s | version {ver} | exportado en {os.path.abspath(a.out)}')
    url = os.environ.get('DATABASE_URL')
    if url:
        import psycopg2
        con = psycopg2.connect(url); cur = con.cursor()
        cur.execute("INSERT INTO training_runs(finished_at,version,n_intents,n_examples,val_acc,train_acc) VALUES (now(),%s,%s,%s,%s,%s)",
                    (ver, len(intents), len(X), val, tr))
        con.commit(); con.close()
    print('RESULT ' + json.dumps(dict(version=ver, val_acc=val, n=len(X))))


if __name__ == '__main__':
    main()
