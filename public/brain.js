// Cerebro de Blu en el navegador: ejecuta la red neuronal propia (pesos entrenados en train/brain.py).
// Sin APIs externas. Los rasgos deben ser IDENTICOS a los de brain.py.
const Brain = (() => {
  let M = null, E, W1, b1, W2, b2;
  const last = {}; let lastReply = '';

  const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim();
  const fnv = s => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; } return h >>> 0; };
  function counts(text) {
    const n = norm(text), toks = n ? n.split(' ') : [], f = [];
    toks.forEach((w, i) => {
      f.push('w:' + w);
      if (i + 1 < toks.length) f.push('b:' + w + '_' + toks[i + 1]);
      const p = '<' + w + '>';
      for (const k of [3, 4, 5]) for (let j = 0; j + k <= p.length; j++) f.push('c:' + p.slice(j, j + k));
    });
    const c = new Map();
    for (const x of f) { const k = fnv(x) % M.B; c.set(k, (c.get(k) || 0) + 1); }
    return c;
  }

  async function load() {
    const [m, w] = await Promise.all([
      fetch('model/model.json', { cache: 'no-store' }).then(r => r.json()),
      fetch('model/weights.bin', { cache: 'no-store' }).then(r => r.arrayBuffer())]);
    const { B, D, H, NI } = m, f = new Float32Array(w); let o = 0;
    const take = n => { const a = f.subarray(o, o + n); o += n; return a; };
    E = take(B * D); W1 = take(D * H); b1 = take(H); W2 = take(H * NI); b2 = take(NI);
    M = m; return m;
  }

  function predict(text) {
    const { D, H, NI } = M, c = counts(text);
    let tot = 0; for (const v of c.values()) tot += v; tot = Math.sqrt(tot) || 1;
    const h0 = new Float32Array(D);
    for (const [k, v] of c) { const w = v / tot, off = k * D; for (let d = 0; d < D; d++) h0[d] += w * E[off + d]; }
    const h1 = new Float32Array(H);
    for (let j = 0; j < H; j++) { let s = b1[j]; for (let d = 0; d < D; d++) s += h0[d] * W1[d * H + j]; h1[j] = Math.tanh(s); }
    const lg = new Float32Array(NI); let mx = -1e9;
    for (let i = 0; i < NI; i++) { let s = b2[i]; for (let j = 0; j < H; j++) s += h1[j] * W2[j * NI + i]; lg[i] = s; if (s > mx) mx = s; }
    let z = 0; for (let i = 0; i < NI; i++) { lg[i] = Math.exp(lg[i] - mx); z += lg[i]; }
    let best = 0; for (let i = 0; i < NI; i++) { lg[i] /= z; if (lg[i] > lg[best]) best = i; }
    return { best, p: lg[best] };
  }

  // ---- memoria y datos del momento ----
  const mem = { get name() { try { return localStorage.getItem('blu_name') || ''; } catch { return ''; } }, set name(v) { try { localStorage.setItem('blu_name', v); } catch {} } };
  const STOP = new Set(['un', 'una', 'el', 'la', 'muy', 'tu', 'de', 'yo', 'tan', 'feliz', 'triste', 'tu', 'amigo', 'bien', 'mal', 'nuevo', 'tu amigo']);
  function extractName(t) {
    const m = t.toLowerCase().match(/(?:me llamo|mi nombre es|soy|me llaman|me dicen|ll[aá]mame|puedes llamarme|yo soy|yo me llamo)\s+([a-záéíóúñü]{2,20})/i);
    if (!m || STOP.has(m[1])) return '';
    return m[1][0].toUpperCase() + m[1].slice(1);
  }
  function horaTxt() {
    const d = new Date(); let h = d.getHours(), m = d.getMinutes();
    const per = h < 6 ? 'de la madrugada' : h < 12 ? 'de la mañana' : h < 19 ? 'de la tarde' : 'de la noche';
    const h12 = h % 12 || 12;
    const pre = h12 === 1 ? 'es la' : 'son las';
    return m === 0 ? `${pre} ${h12} ${per} en punto` : `${pre} ${h12} con ${m} minutos ${per}`;
  }
  const fechaTxt = () => new Date().toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long' });

  function pick(it) {
    const r = it.replies; if (r.length === 1) return r[0];
    let i, n = 0; do { i = Math.floor(Math.random() * r.length); } while (i === last[it.tag] && ++n < 6);
    last[it.tag] = i; return r[i];
  }

  function reply(text, ctx = {}) {
    if (!M) return { tag: 'no_entiendo', conf: 0, text: 'Todavía estoy despertando mi cerebro, dame un segundito.', emotion: 'thinking', low: true };
    const { best, p } = predict(text);
    let it = M.intents[best], low = p < M.threshold;
    const real = { tag: it.tag, conf: p };
    if (low) it = M.intents.find(x => x.tag === 'no_entiendo') || it;
    let r = pick(it), out;
    switch (it.tag) {
      case 'repetir': out = lastReply ? 'Te lo repito. ' + lastReply : 'Todavía no he dicho nada, ¿qué quieres saber?'; break;
      case 'nombre_usuario': { const n = extractName(text); if (n) mem.name = n; out = n ? r.t : 'No alcancé a oír bien tu nombre. ¿Me lo repites?'; break; }
      case 'mi_nombre': out = mem.name ? r.t : 'Todavía no me has dicho tu nombre. ¿Cómo te llamas?'; break;
      case 'que_ves': out = ctx.vision || 'No puedo ver nada ahorita.'; break;
      default: out = r.t;
    }
    out = out.replace('{nombre}', mem.name || 'amigo').replace('{hora}', horaTxt()).replace('{fecha}', fechaTxt());
    if (it.tag !== 'repetir') lastReply = out;
    return { tag: real.tag, conf: real.conf, text: out, emotion: r.e, low };
  }

  return { load, reply, get version() { return M && M.version; }, get info() { return M; } };
})();
