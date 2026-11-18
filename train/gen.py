"""Generador de respuestas de Blu: una red neuronal propia (GRU) entrenada desde cero que ESCRIBE palabra por palabra.

  texto de la persona -> rasgos hash (los mismos de brain.py) -> vector de contexto
        -> decodificador GRU que genera la respuesta (palabra a palabra) + cabeza de emoción

Se entrena con los datos de PostgreSQL (frases y respuestas escritas por humanos).  Aprende el estilo de Blu y
combina lo aprendido para decir cosas nuevas.  Exporta pesos (float16) que el navegador ejecuta con gen.js.
Uso:  python gen.py [--epochs 30]
"""
import os, sys, re, json, time, math, random, argparse
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brain as BR

EMO = ['neutral', 'happy', 'sad', 'surprised', 'thinking', 'love', 'angry', 'listening', 'sleepy']
PAD, BOS, EOS, UNK = 0, 1, 2, 3
NOGEN = {'crisis', 'no_entiendo', 'repetir'}        # respuestas delicadas: nunca se generan, siempre se eligen escritas

TOK = re.compile(r"\{[a-z]+\}|[a-záéíóúüñ0-9]+|[.,;:!?¿¡…]")
def tok(s): return TOK.findall(s.lower())

PROPER = {'blu': 'Blu', 'jessito': 'Jessito', 'jesús': 'Jesús', 'méxico': 'México', 'vida': 'Vida', 'línea': 'Línea'}
def detok(t):
    out, cap = '', True
    for i, w in enumerate(t):
        if w in '.,;:!?…' and i:
            out += w; cap = w in '.!?…'; continue
        if w in '¿¡':
            out += (' ' if out and not out.endswith(' ') else '') + w; cap = False; continue
        word = PROPER.get(w, w)
        if cap: word = word[0].upper() + word[1:]
        out += ('' if (not out or out.endswith(('¿', '¡'))) else ' ') + word
        cap = False
    return out

# frases que se combinan con las respuestas base para que Blu aprenda a variar y a conversar
OPEN = {
 'sad': ['Lo siento mucho.', 'Ay, qué difícil.', 'Te entiendo.', 'Estoy contigo.', 'Uy, eso suena duro.'],
 'listening': ['Te escucho.', 'Aquí estoy.', 'Cuéntame.', 'Entiendo.'],
 'happy': ['Qué bien.', 'Qué bonito.', 'Me alegra.', 'Qué padre.', 'Genial.', 'Jeje.'],
 'love': ['Ay, qué lindo.', 'Me encanta.', 'Qué ternura.', 'Gracias, de verdad.'],
 'surprised': ['Wow.', 'Ay, qué sorpresa.', 'No lo puedo creer.'],
 'thinking': ['Mmm.', 'A ver.', 'Déjame pensar.', 'Buena pregunta.'],
 'sleepy': ['Ay, qué sueño.', 'Con calma.', 'Despacito.'],
 'neutral': ['Claro.', 'Va.', 'Listo.'],
 'angry': ['Entiendo.', 'Respira.']}
FOLLOW = {
 'sad': ['¿Quieres contarme más?', '¿Cómo te sientes ahora?', 'Aquí sigo contigo.', 'Respira conmigo un poquito.'],
 'listening': ['¿Qué más pasó?', 'Sigue, te escucho.', '¿Y cómo te hizo sentir?'],
 'happy': ['¿Y tú cómo estás?', 'Cuéntame más.', '¿Qué más me cuentas?', 'Eso me pone contento.'],
 'love': ['Eres muy especial.', 'Me haces muy feliz.'],
 'surprised': ['¿De verdad?', 'Cuéntame más.'],
 'thinking': ['¿Tú qué piensas?', '¿Tú qué opinas?'],
 'sleepy': ['Descansa un poquito.'],
 'neutral': ['¿Qué más hacemos?', 'Dime.'],
 'angry': ['Aquí estoy contigo.']}

def variant(t, e, rng):
    m = rng.random()
    out = t
    if m >= .5 and m < .7 or m >= .9:                      # con apertura
        o = rng.choice(OPEN.get(e, OPEN['happy']))
        if o.split()[0].lower() != t.split()[0].lower(): out = o + ' ' + out
    if m >= .7 and not t.rstrip().endswith('?'):           # con pregunta/cierre
        out = out + ' ' + rng.choice(FOLLOW.get(e, FOLLOW['happy']))
    return out

# ---------------- modelo ----------------
class G(nn.Module):
    def __init__(s, V, B, D, H, Ed):
        super().__init__()
        s.bag = nn.EmbeddingBag(B, D, mode='sum'); s.fc = nn.Linear(D, H); s.emo = nn.Linear(H, len(EMO))
        s.init = nn.Linear(H, H); s.emb = nn.Embedding(V, Ed, padding_idx=PAD)
        s.gru = nn.GRU(Ed + H, H, batch_first=True); s.out = nn.Linear(H, V); s.dp = nn.Dropout(.15)
        nn.init.normal_(s.bag.weight, 0, .1)
    def encode(s, idx, off, w):
        return torch.tanh(s.fc(s.bag(idx, off, per_sample_weights=w)))
    def forward(s, idx, off, w, inp):
        c = s.dp(s.encode(idx, off, w))
        h = torch.tanh(s.init(c)).unsqueeze(0)
        x = torch.cat([s.dp(s.emb(inp)), c.unsqueeze(1).expand(-1, inp.size(1), -1)], -1)
        o, _ = s.gru(x, h)
        return s.out(s.dp(o)), s.emo(c)

def batchify(counts):
    idx, off, w = [], [], []
    for c in counts:
        off.append(len(idx)); tot = math.sqrt(sum(c.values())) or 1.0
        for k, v in c.items(): idx.append(k); w.append(v / tot)
    if not idx: idx, w = [0], [0.0]
    return torch.tensor(idx), torch.tensor(off), torch.tensor(w, dtype=torch.float32)

# ---------------- generación (igual que en gen.js) ----------------
@torch.no_grad()
def generate(m, text, itos, rng, temp=.7, top_p=.92, maxlen=40):
    m.eval()
    c = m.encode(*batchify([BR.feature_counts(text)]))
    h = torch.tanh(m.init(c)).unsqueeze(0)
    prev, out, lp = BOS, [], 0.0
    for t in range(maxlen):
        x = torch.cat([m.emb(torch.tensor([[prev]])), c.unsqueeze(1)], -1)
        o, h = m.gru(x, h)
        lg = m.out(o[:, 0])[0]
        lg[[PAD, BOS, UNK]] = -1e9
        if t < 3: lg[EOS] = -1e9
        if out: lg[out[-1]] = -1e9                      # nada de repetir la misma palabra seguida
        logp = F.log_softmax(lg, -1)
        p = F.softmax(lg / temp, -1)
        sp, si = p.sort(descending=True)
        keep = (sp.cumsum(0) - sp) < top_p
        sp = sp * keep; sp /= sp.sum()
        nxt = si[torch.multinomial(sp, 1, generator=None)].item()
        lp += logp[nxt].item()
        if nxt == EOS: break
        out.append(nxt); prev = nxt
    emo = F.softmax(m.emo(c)[0], -1)
    return detok([itos[i] for i in out]), lp / max(1, len(out) + 1), EMO[int(emo.argmax())], float(emo.max())

def export(m, vocab, out, ver, meta):
    os.makedirs(out, exist_ok=True)
    sd = m.state_dict()
    order = ['bag.weight', 'fc.weight', 'fc.bias', 'emo.weight', 'emo.bias', 'init.weight', 'init.bias', 'emb.weight',
             'gru.weight_ih_l0', 'gru.weight_hh_l0', 'gru.bias_ih_l0', 'gru.bias_hh_l0', 'out.weight', 'out.bias']
    blob = b''.join(sd[k].detach().cpu().numpy().astype('<f2').tobytes() for k in order)
    tmp = os.path.join(out, 'gen.bin.tmp'); open(tmp, 'wb').write(blob); os.replace(tmp, os.path.join(out, 'gen.bin'))
    cfg = dict(version=ver, V=len(vocab), B=BR.B, D=m.fc.in_features, H=m.fc.out_features, Ed=m.emb.embedding_dim,
               vocab=vocab, emotions=EMO, order=order, **meta)
    tmp = os.path.join(out, 'gen.json.tmp'); json.dump(cfg, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
    os.replace(tmp, os.path.join(out, 'gen.json'))
    vp = os.path.join(os.path.dirname(os.path.abspath(out)), 'version.json')
    cur = {}
    try: cur = json.load(open(vp))
    except Exception: pass
    cur['gen'] = ver; cur.setdefault('app', 'dev'); cur.setdefault('model', '0')
    cur['version'] = f"{cur['app']}.{cur['model']}.{cur['gen']}"
    json.dump(cur, open(vp + '.tmp', 'w')); os.replace(vp + '.tmp', vp)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'model'))
    ap.add_argument('--epochs', type=int, default=30)
    ap.add_argument('--per', type=int, default=3, help='respuestas por frase en cada época')
    ap.add_argument('--H', type=int, default=256)
    ap.add_argument('--seed', type=int, default=11)
    a = ap.parse_args()
    t0 = time.time(); rng = random.Random(a.seed); torch.manual_seed(a.seed); torch.set_num_threads(os.cpu_count() or 4)

    intents, src = BR.load_data()
    use = [i for i in intents if i['users'] and i['replies'] and i['tag'] not in NOGEN and not any('{' in t for t, _ in i['replies'])]
    print(f'datos: {src} | intenciones para generar={len(use)} frases={sum(len(i["users"]) for i in use)} respuestas={sum(len(i["replies"]) for i in use)}')

    # vocabulario con TODAS las variantes posibles
    cnt = {}
    texts = [t for i in use for t, _ in i['replies']] + [o for v in OPEN.values() for o in v] + [f for v in FOLLOW.values() for f in v]
    for s in texts:
        for w in tok(s): cnt[w] = cnt.get(w, 0) + 1
    vocab = ['<pad>', '<bos>', '<eos>', '<unk>'] + sorted(cnt)
    stoi = {w: i for i, w in enumerate(vocab)}
    print(f'vocabulario: {len(vocab)} palabras')

    hold = {}
    for it in use:
        if len(it['users']) >= 12:
            hold[it['tag']] = rng.sample(it['users'], max(1, len(it['users']) // 14))
    holdset = {u for v in hold.values() for u in v}

    m = G(len(vocab), BR.B, 96, a.H, 128)
    print(f'parametros: {sum(p.numel() for p in m.parameters()) / 1e6:.2f} millones')
    opt = torch.optim.AdamW(m.parameters(), lr=2e-3, weight_decay=1e-4)
    pairs_all = [(u, it) for it in use for u in it['users'] if u not in holdset]
    steps_total = a.epochs * math.ceil(len(pairs_all) * a.per / 64); step = 0

    for ep in range(a.epochs):
        m.train(); data = []
        for u, it in pairs_all:
            for t, e in rng.sample(it['replies'], min(a.per, len(it['replies']))) if len(it['replies']) >= a.per else [rng.choice(it['replies']) for _ in range(a.per)]:
                x = BR.augment(u, rng) if rng.random() < .6 else u
                y = [BOS] + [stoi.get(w, UNK) for w in tok(variant(t, e, rng))][:38] + [EOS]
                data.append((x, y, EMO.index(e) if e in EMO else 1))
        rng.shuffle(data)
        data.sort(key=lambda d: len(d[1]) + rng.random() * 6)            # lotes de longitud parecida
        batches = [data[i:i + 64] for i in range(0, len(data), 64)]; rng.shuffle(batches)
        tot = 0.0
        for b in batches:
            lr = 2e-3 * (.5 * (1 + math.cos(math.pi * step / steps_total)) * .95 + .05); step += 1
            for g in opt.param_groups: g['lr'] = lr
            idx, off, w = batchify([BR.feature_counts(x) for x, _, _ in b])
            L = max(len(y) for _, y, _ in b)
            Y = torch.tensor([y + [PAD] * (L - len(y)) for _, y, _ in b])
            logits, emo = m(idx, off, w, Y[:, :-1])
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), Y[:, 1:].reshape(-1), ignore_index=PAD) \
                 + .5 * F.cross_entropy(emo, torch.tensor([e for _, _, e in b]))
            opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step(); tot += loss.item()
        if ep % 5 == 0 or ep == a.epochs - 1:
            print(f'  epoca {ep + 1:3d}/{a.epochs}  perdida {tot / len(batches):.3f}  ({time.time() - t0:.0f}s)', flush=True)

    # ---- evaluación con frases NUNCA vistas ----
    itos = vocab; samples = []
    print('--- ejemplos con frases nuevas ---')
    r2 = random.Random(5)
    for tag, us in list(hold.items())[:40]:
        u = us[0]; txt, lp, emo, ep_ = generate(m, u, itos, r2)
        samples.append(lp); print(f'[{tag}] "{u}" -> ({emo} {ep_:.2f}, logp {lp:.2f}) {txt}')
    emo_ok = 0; emo_n = 0
    for it in use:
        if it['tag'] in hold:
            for u in hold[it['tag']]:
                c = m.encode(*batchify([BR.feature_counts(u)])); pe = EMO[int(m.emo(c)[0].argmax())]
                emo_n += 1; emo_ok += pe in {e for _, e in it['replies']}
    print(f'emocion correcta en frases nuevas: {emo_ok}/{emo_n} = {100 * emo_ok / max(1, emo_n):.1f}%')
    med = float(np.median(samples)) if samples else -1.5
    ver = time.strftime('%Y%m%d%H%M%S')
    export(m, vocab, a.out, ver, dict(min_logp=round(min(-0.9, med - 0.45), 2), n_pairs=len(pairs_all), trained_at=time.strftime('%Y-%m-%d %H:%M:%S'),
                                      emo_acc=round(emo_ok / max(1, emo_n), 3)))
    url = os.environ.get('DATABASE_URL')
    if url:
        import psycopg2
        con = psycopg2.connect(url); cur = con.cursor()
        cur.execute("INSERT INTO training_runs(finished_at,version,n_intents,n_examples,notes) VALUES (now(),%s,%s,%s,'generador')", (ver, len(use), len(pairs_all)))
        con.commit(); con.close()
    print(f'listo en {time.time() - t0:.0f}s | generador {ver} | exportado en {os.path.abspath(a.out)}')
    print('RESULT ' + json.dumps(dict(version=ver, emo_acc=emo_ok / max(1, emo_n))))

if __name__ == '__main__':
    main()
