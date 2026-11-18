// Generador de respuestas de Blu (red neuronal GRU propia, entrenada con train/gen.py).
// Escribe la respuesta palabra por palabra en el navegador, condicionada por lo que dijiste y por la intención detectada.
const Gen = (() => {
  let C = null, P = null;
  const PAD = 0, BOS = 1, EOS = 2, UNK = 3;
  const h2f = (() => {                                   // float16 -> float32
    const t = new Float32Array(65536);
    for (let h = 0; h < 65536; h++) { const s = h & 0x8000 ? -1 : 1, e = (h >> 10) & 31, f = h & 1023; t[h] = e === 0 ? s * Math.pow(2, -14) * (f / 1024) : e === 31 ? (f ? NaN : s * Infinity) : s * Math.pow(2, e - 15) * (1 + f / 1024); }
    return t;
  })();

  async function load() {
    const [cfg, buf] = await Promise.all([
      fetch('model/gen.json', { cache: 'no-store' }).then(r => r.json()),
      fetch('model/gen.bin', { cache: 'no-store' }).then(r => r.arrayBuffer())]);
    const u = new Uint16Array(buf), { B, D, H, Ed, V, Ti } = cfg, NT = cfg.tags.length;
    const size = { 'bag.weight': B * D, 'fc.weight': H * D, 'fc.bias': H, 'emo.weight': 9 * (H + Ti), 'emo.bias': 9, 'init.weight': H * (H + Ti), 'init.bias': H,
      'emb.weight': V * Ed, 'gru.weight_ih_l0': 3 * H * (Ed + H + Ti), 'gru.weight_hh_l0': 3 * H * H, 'gru.bias_ih_l0': 3 * H, 'gru.bias_hh_l0': 3 * H,
      'out.weight': V * H, 'out.bias': V, 'intent.weight': (NT + 1) * Ti };
    let o = 0; const W = {};
    for (const k of cfg.order) { const n = size[k], a = new Float32Array(n); for (let i = 0; i < n; i++) a[i] = h2f[u[o + i]]; o += n; W[k] = a; }
    cfg.tagIdx = Object.fromEntries(cfg.tags.map((t, i) => [t, i]));
    C = cfg; P = W; return cfg;
  }

  const PROPER = { blu: 'Blu', jessito: 'Jessito', 'jesús': 'Jesús', 'méxico': 'México', vida: 'Vida', 'línea': 'Línea' };
  function detok(t) {
    let out = '', cap = true;
    t.forEach((w, i) => {
      if (/^[.,;:!?…]$/.test(w) && i) { out += w; cap = /[.!?…]/.test(w); return; }
      if (w === '¿' || w === '¡') { out += (out && !out.endsWith(' ') ? ' ' : '') + w; return; }
      let word = PROPER[w] || w; if (cap) word = word[0].toUpperCase() + word.slice(1);
      out += (!out || out.endsWith('¿') || out.endsWith('¡') ? '' : ' ') + word; cap = false;
    });
    return out;
  }

  const sig = x => 1 / (1 + Math.exp(-x));
  function run(text, tag, temp, topP, maxLen) {
    const { D, H, Ed, V, Ti } = C, I = Ed + H + Ti, ti = C.tagIdx[tag];
    // encoder (mismos rasgos que el clasificador)
    const cnt = Brain.features(text); let tot = 0; for (const v of cnt.values()) tot += v; tot = Math.sqrt(tot) || 1;
    const h0 = new Float32Array(D), bag = P['bag.weight'];
    for (const [k, v] of cnt) { const w = v / tot, off = k * D; for (let d = 0; d < D; d++) h0[d] += w * bag[off + d]; }
    const z = new Float32Array(H + Ti), fcW = P['fc.weight'], fcB = P['fc.bias'];
    for (let j = 0; j < H; j++) { let s = fcB[j]; for (let d = 0; d < D; d++) s += fcW[j * D + d] * h0[d]; z[j] = Math.tanh(s); }
    z.set(P['intent.weight'].subarray(ti * Ti, (ti + 1) * Ti), H);
    // cabeza de emoción
    const ew = P['emo.weight'], eb = P['emo.bias'], el = new Float32Array(9); let em = -1e9;
    for (let e = 0; e < 9; e++) { let s = eb[e]; for (let c = 0; c < H + Ti; c++) s += ew[e * (H + Ti) + c] * z[c]; el[e] = s; if (s > em) em = s; }
    let es = 0; for (let e = 0; e < 9; e++) { el[e] = Math.exp(el[e] - em); es += el[e]; }
    let eBest = 0; for (let e = 0; e < 9; e++) if (el[e] > el[eBest]) eBest = e;
    // estado inicial del decodificador
    let h = new Float32Array(H); const iw = P['init.weight'], ib = P['init.bias'];
    for (let j = 0; j < H; j++) { let s = ib[j]; for (let c = 0; c < H + Ti; c++) s += iw[j * (H + Ti) + c] * z[c]; h[j] = Math.tanh(s); }
    // parte constante de W_ih * [emb, z]
    const wih = P['gru.weight_ih_l0'], whh = P['gru.weight_hh_l0'], bih = P['gru.bias_ih_l0'], bhh = P['gru.bias_hh_l0'];
    const zpart = new Float32Array(3 * H);
    for (let r = 0; r < 3 * H; r++) { let s = bih[r]; const off = r * I + Ed; for (let c = 0; c < H + Ti; c++) s += wih[off + c] * z[c]; zpart[r] = s; }
    const emb = P['emb.weight'], ow = P['out.weight'], ob = P['out.bias'];
    const gh = new Float32Array(3 * H), lg = new Float32Array(V), out = [];
    let prev = BOS, lp = 0;
    for (let t = 0; t < maxLen; t++) {
      for (let r = 0; r < 3 * H; r++) { let s = bhh[r]; const off = r * H; for (let c = 0; c < H; c++) s += whh[off + c] * h[c]; gh[r] = s; }
      const eo = prev * Ed, nh = new Float32Array(H);
      for (let j = 0; j < H; j++) {
        let gr = zpart[j] + gh[j], gz = zpart[H + j] + gh[H + j], gn = zpart[2 * H + j];
        const o1 = j * I, o2 = (H + j) * I, o3 = (2 * H + j) * I;
        for (let c = 0; c < Ed; c++) { const x = emb[eo + c]; gr += wih[o1 + c] * x; gz += wih[o2 + c] * x; gn += wih[o3 + c] * x; }
        const r = sig(gr), zz = sig(gz), n = Math.tanh(gn + r * gh[2 * H + j]);
        nh[j] = (1 - zz) * n + zz * h[j];
      }
      h = nh;
      let mx = -1e9;
      for (let v = 0; v < V; v++) { let s = ob[v]; const off = v * H; for (let c = 0; c < H; c++) s += ow[off + c] * h[c]; lg[v] = s; }
      lg[PAD] = lg[BOS] = lg[UNK] = -1e9; if (t < 3) lg[EOS] = -1e9; if (out.length) lg[out[out.length - 1]] = -1e9;
      for (let v = 0; v < V; v++) if (lg[v] > mx) mx = lg[v];
      let zsum = 0; const p = new Float32Array(V), q = new Float32Array(V);
      for (let v = 0; v < V; v++) { p[v] = Math.exp(lg[v] - mx); zsum += p[v]; }
      let zt = 0; for (let v = 0; v < V; v++) { q[v] = Math.exp((lg[v] - mx) / temp); zt += q[v]; }
      // top-p
      const ids = Array.from({ length: V }, (_, i) => i).filter(i => q[i] > 1e-6).sort((a, b) => q[b] - q[a]);
      let cum = 0, keep = []; for (const i of ids) { if (cum >= topP * zt) break; keep.push(i); cum += q[i]; }
      let ks = 0; for (const i of keep) ks += q[i]; let rr = Math.random() * ks, tok = keep[0];
      for (const i of keep) { rr -= q[i]; if (rr <= 0) { tok = i; break; } }
      lp += Math.log(p[tok] / zsum + 1e-12);
      if (tok === EOS) break;
      out.push(tok); prev = tok;
    }
    return { toks: out.map(i => C.vocab[i]), logp: lp / Math.max(1, out.length + 1), emotion: C.emotions[eBest], emoP: el[eBest] / es };
  }

  function ok(g) {                                          // filtros de calidad: si algo se ve raro, se descarta
    if (g.toks.length < 3 || g.toks.length > 38 || g.logp < (C.min_logp ?? -0.9)) return false;
    if (g.toks.includes('<unk>')) return false;
    const sents = g.text.split(/(?<=[.!?…])\s+/).map(s => s.trim()).filter(Boolean);
    if (sents.length > 5) return false;
    const seen = new Set();
    for (let i = 0; i < sents.length; i++) {
      const k = sents[i].toLowerCase(); if (seen.has(k)) return false; seen.add(k);
      if (i && sents[i].split(/\s+/).length <= 2 && sents[i - 1].split(/\s+/).length <= 2) return false;   // dos muletillas seguidas
    }
    return true;
  }

  function generate(text, tag, { temp = 0.7, topP = 0.92, maxLen = 40, tries = 3 } = {}) {
    if (!C || C.tagIdx[tag] === undefined) return null;
    for (let k = 0; k < tries; k++) {
      const g = run(text, tag, temp, topP, maxLen); g.text = detok(g.toks);
      if (ok(g)) return g;
    }
    return null;
  }
  return { load, generate, get ready() { return !!C; }, get info() { return C; } };
})();
