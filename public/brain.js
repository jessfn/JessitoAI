// Cerebro de Blu en el navegador: red neuronal propia (pesos entrenados en train/brain.py) + memoria + contexto.
// Sin APIs externas. Los rasgos deben ser IDENTICOS a los de brain.py.
const Brain = (() => {
  let M = null, E, W1, b1, W2, b2;
  const lastIdx = {}; let lastReply = '', prevTag = '';

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

  // ======================= MEMORIA (recuerdos) =======================
  const lsGet = (k, d) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } };
  const lsSet = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };
  const device = (() => { let d = ''; try { d = localStorage.getItem('blu_dev') || ''; } catch {} if (!d) { d = Math.random().toString(36).slice(2) + Date.now().toString(36); try { localStorage.setItem('blu_dev', d); } catch {} } return d; })();
  const fresh = () => ({ facts: {}, likes: [], dislikes: [], family: {}, notes: [], moods: [], turns: [], created: Date.now(), lastSeen: 0 });
  let mem = Object.assign(fresh(), lsGet('blu_mem', {}));
  if (!mem.facts.name) { try { const n = localStorage.getItem('blu_name'); if (n) mem.facts.name = n; } catch {} }   // compatibilidad
  let syncT = 0;
  function save() {
    mem.lastSeen = Date.now(); lsSet('blu_mem', mem);
    if (Date.now() - syncT > 20000) {                                        // respaldo en el servidor (PostgreSQL)
      syncT = Date.now();
      fetch('/api/memory', { method: 'POST', headers: { 'content-type': 'application/json' }, keepalive: true, body: JSON.stringify({ device, memory: mem }) }).catch(() => {});
    }
  }
  const cap = (a, n) => { while (a.length > n) a.shift(); return a; };
  const addUnique = (a, v, n) => { if (v && !a.includes(v)) a.push(v); cap(a, n); };
  const cleanPhrase = s => s.replace(/\s+/g, ' ').trim();
  const MOOD = { triste_usuario: 'triste', soledad: 'solo', feliz_usuario: 'feliz', enojo_usuario: 'enojado', frustracion: 'frustrado', estres: 'estresado', cansado: 'cansado',
    miedo_usuario: 'con miedo', fracaso: 'desanimado', logro: 'orgulloso', enfermo: 'mal de salud', esperanza: 'esperanzado', anticipacion: 'emocionado', autoestima: 'inseguro',
    culpa: 'con culpa', verguenza: 'con pena', decepcion: 'decepcionado', nostalgia: 'nostálgico', celos: 'con celos', amor: 'enamorado', confusion: 'confundido', dormir_mal: 'desvelado' };
  const NEGMOOD = new Set(['triste', 'solo', 'enojado', 'frustrado', 'estresado', 'con miedo', 'desanimado', 'mal de salud', 'inseguro', 'con culpa', 'con pena', 'decepcionado', 'con celos', 'desvelado']);

  function extractName(t) {
    const m = t.toLowerCase().match(/(?:me llamo|mi nombre es|soy|me llaman|me dicen|ll[aá]mame|puedes llamarme|yo soy|yo me llamo)\s+([a-záéíóúñü]{2,20})/i);
    const STOP = ['un', 'una', 'el', 'la', 'muy', 'tu', 'de', 'yo', 'tan', 'feliz', 'triste', 'amigo', 'bien', 'mal', 'nuevo'];
    if (!m || STOP.includes(m[1])) return '';
    return m[1][0].toUpperCase() + m[1].slice(1);
  }
  function learn(text, tag) {
    const nt = text.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''), f = mem.facts;
    let m;
    if (tag === 'nombre_usuario') { const n = extractName(text); if (n) f.name = n; }
    if ((m = nt.match(/tengo (?:un|una|dos|tres)?\s*(perro|perrito|perra|gato|gatito|gata|pajaro|conejo|hamster|pez|tortuga|loro|caballo)(?:.*?(?:se llama|llamado|llamada|le puse)\s+([a-z]{2,15}))?/)))
      f.pet = { type: m[1], name: m[2] ? m[2][0].toUpperCase() + m[2].slice(1) : (f.pet && f.pet.type === m[1] ? f.pet.name : '') };
    else if ((m = nt.match(/mi (perro|perrito|perra|gato|gatito|gata|pajaro|conejo|hamster|pez|tortuga|loro|caballo) se llama ([a-z]{2,15})/)))
      f.pet = { type: m[1], name: m[2][0].toUpperCase() + m[2].slice(1) };
    if ((m = nt.match(/me (?:gusta|gustan|encanta|encantan|fascina|fascinan)\s+(?:mucho\s+)?(?:el |la |los |las |un |una )?([a-z ]{3,28}?)(?:\s+(?:y|pero|porque|cuando|que|por)\b|[.,!?]|$)/))) {
      const v = cleanPhrase(m[1]); if (!/contigo|hablar|platicar|escucharte|tu voz/.test(v)) addUnique(mem.likes, v, 15);
    }
    if ((m = nt.match(/(?:odio|detesto|no me gusta|no me gustan)\s+(?:el |la |los |las )?([a-z ]{3,28}?)(?:\s+(?:y|pero|porque)\b|[.,!?]|$)/))) addUnique(mem.dislikes, cleanPhrase(m[1]), 10);
    if ((m = nt.match(/mi (mama|papa|hermano|hermana|abuela|abuelo|hijo|hija|novia|novio|esposa|esposo|tia|tio|primo|prima)(?: se llama ([a-z]{2,15}))?/)))
      mem.family[m[1]] = m[2] ? m[2][0].toUpperCase() + m[2].slice(1) : (mem.family[m[1]] || true);
    if ((m = nt.match(/trabajo (?:en|de|como|para) ([a-z ]{3,25}?)(?:[.,!?]|$| y )/))) f.job = cleanPhrase(m[1]);
    if ((m = nt.match(/(?:estudio|estoy estudiando) ([a-z ]{3,25}?)(?:[.,!?]|$| y )/))) f.study = cleanPhrase(m[1]);
    if ((m = nt.match(/vivo en ([a-z ]{3,25}?)(?:[.,!?]|$| y )/))) f.city = cleanPhrase(m[1]);
    if ((m = nt.match(/(?:mi cumple(?:anos)? es|cumplo anos)(?: el| en)? ([a-z0-9 ]{3,22})/))) f.birthday = cleanPhrase(m[1]);
    if (tag === 'recordar_esto' && (m = text.match(/(?:recuerda que|anota que|guarda que|no se te olvide que|toma nota de que|recuerda esto:?|anota esto:?)\s*(.{3,160})/i))) addUnique(mem.notes, m[1].trim(), 20);
    if (MOOD[tag]) { cap(mem.moods, 30); mem.moods.push({ m: MOOD[tag], t: Date.now() }); }
  }
  const lastMood = (maxAgeH = 72) => { const x = mem.moods[mem.moods.length - 1]; return x && Date.now() - x.t < maxAgeH * 3600e3 ? x : null; };
  const join = a => a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' y ' + a[a.length - 1];
  const RELN = { mama: 'mamá', papa: 'papá', tia: 'tía', tio: 'tío' };
  const rel = r => RELN[r] || r;

  function memoriaTxt() {
    const f = mem.facts, p = [];
    if (f.name) p.push(`te llamas ${f.name}`);
    if (f.pet) p.push(`tienes ${f.pet.type === 'perro' || f.pet.type === 'perrito' ? 'un perrito' : 'un ' + f.pet.type}${f.pet.name ? ' que se llama ' + f.pet.name : ''}`);
    if (mem.likes.length) p.push(`te gusta ${join(mem.likes.slice(-3))}`);
    const fam = Object.entries(mem.family).slice(0, 3).map(([r, n]) => `tu ${rel(r)}${n && n !== true ? ' ' + n : ''}`);
    if (fam.length) p.push(`me hablaste de ${join(fam)}`);
    if (f.job) p.push(`trabajas en ${f.job}`); if (f.study) p.push(`estudias ${f.study}`); if (f.city) p.push(`vives en ${f.city}`);
    if (f.birthday) p.push(`tu cumpleaños es ${f.birthday}`);
    if (mem.notes.length) p.push(`me pediste recordar que ${mem.notes[mem.notes.length - 1]}`);
    const lm = lastMood(); if (lm) p.push(`la última vez te sentías ${lm.m}`);
    return p.length ? 'Recuerdo que ' + join(p) + '. Y todo lo que me cuentas lo guardo con cariño.' : 'Todavía no sé mucho de ti. Cuéntame cosas, como tu nombre, qué te gusta o si tienes mascotas, y las guardo en mi memoria.';
  }
  function recallLine() {
    const f = mem.facts, lm = lastMood(72), r = Math.random();
    if (lm && NEGMOOD.has(lm.m) && !lm.asked && Date.now() - lm.t > 30 * 60e3) { lm.asked = true; return `Oye, la última vez me dijiste que te sentías ${lm.m}. ¿Cómo sigues hoy?`; }
    if (f.pet && r < .5) return `¿Y cómo está ${f.pet.name || 'tu ' + f.pet.type}?`;
    const fam = Object.entries(mem.family); if (fam.length && r < .65) { const [rl, n] = fam[Math.floor(Math.random() * fam.length)]; return `¿Cómo está tu ${rel(rl)}${n && n !== true ? ' ' + n : ''}?`; }
    if (mem.likes.length && r < .8) return `Por cierto, me acordé de que te gusta ${mem.likes[Math.floor(Math.random() * mem.likes.length)]}.`;
    if (f.study && r < .9) return `¿Cómo vas con ${f.study}?`;
    if (f.job) return `¿Cómo va el trabajo?`;
    return '';
  }

  // ======================= SENTIDO COMÚN DE CONVERSACIÓN =======================
  const NEG = /\b(mal|malo|mala|horrible|triste|feo|fea|odio|dolor|duele|cansad[oa]|solo|sola|miedo|llorar|llore|problema|pelea|pelee|perdi|muerte|murio|enfermo|enferma|estres|dificil|pesado|pesada|terrible|peor|harto|harta|coraje|rabia|ansiedad|preocupa|preocupado|nervios|nervioso|vacio|culpa|error|fracaso|nadie|nunca|injusto|injusta|me regano|me grito|me dejo|me dejaron|rompieron|extrano)\b/;
  const POS = /\b(bien|bueno|buena|feliz|increible|genial|padre|chido|gane|logre|amo|encanta|bonito|bonita|excelente|lindo|linda|alegre|contento|contenta|emocionado|emocionada|divertido|divertida|maravilloso|maravillosa|mejor|gracias|exito|premio|aprobe|pase|me dieron|me aceptaron|viaje|fiesta|cumpleanos)\b/;
  const EMPATHY = new Set(['triste_usuario', 'soledad', 'enojo_usuario', 'frustracion', 'estres', 'trabajo', 'fracaso', 'enfermo', 'miedo_usuario', 'cansado', 'decepcion', 'culpa', 'verguenza', 'celos', 'nostalgia', 'autoestima', 'crisis', 'dinero', 'imprevisto', 'cita_medica', 'mascota_cuidado', 'dormir_mal', 'insulto', 'enojo_usuario']);
  const JOY = new Set(['feliz_usuario', 'logro', 'esperanza', 'anticipacion', 'amigos_salida', 'viaje', 'ejercicio', 'apariencia', 'estudios_logros', 'amor', 'cumpleanos', 'te_quiero', 'cumplido']);
  const QSTART = /^(que|como|cuando|donde|por que|porque|cual|cuales|quien|quienes|cuanto|cuantos|cuanta|cuantas|sabes|puedes|existe|es verdad|es cierto|crees que)\b/;
  const LAUGH = /\b(ja|jaja|jajaja|jeje|jejeje|lol|xd|haha)\b|jaja/;
  const TH_LOW = 0.55;

  function pickFrom(list, key) {
    if (list.length === 1) return list[0];
    let i, n = 0; do { i = Math.floor(Math.random() * list.length); } while (i === lastIdx[key] && ++n < 8);
    lastIdx[key] = i; return list[i];
  }
  function continuation(text) {          // si no entiende del todo, responde con empatía o curiosidad como una persona
    const nt = norm(text), words = nt ? nt.split(' ').length : 0, pools = M.pools || {};
    const neg = (nt.match(new RegExp(NEG.source, 'g')) || []).length, pos = (nt.match(new RegExp(POS.source, 'g')) || []).length;
    let key = null;
    if (LAUGH.test(nt) && words <= 4) key = 'cont_humor';
    else if (QSTART.test(nt)) key = 'cont_pregunta';
    else if (neg > pos || (neg === pos && EMPATHY.has(prevTag) && words >= 3)) key = neg || EMPATHY.has(prevTag) ? 'cont_empatia' : null;
    else if (pos > neg || (JOY.has(prevTag) && words >= 3)) key = 'cont_alegria';
    else if (words >= 4) key = 'cont_curioso';
    return key && pools[key] ? { key, r: pickFrom(pools[key], key) } : null;
  }

  // ======================= RESPUESTA =======================
  const horaTxt = () => { const d = new Date(), h = d.getHours(), m = d.getMinutes(); const per = h < 6 ? 'de la madrugada' : h < 12 ? 'de la mañana' : h < 19 ? 'de la tarde' : 'de la noche'; const h12 = h % 12 || 12, pre = h12 === 1 ? 'es la' : 'son las'; return m === 0 ? `${pre} ${h12} ${per} en punto` : `${pre} ${h12} con ${m} minutos ${per}`; };
  const fechaTxt = () => new Date().toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long' });
  const pick = it => it.replies.length === 1 ? it.replies[0] : it.replies[(() => { let i, n = 0; do { i = Math.floor(Math.random() * it.replies.length); } while (i === lastIdx[it.tag] && ++n < 8); lastIdx[it.tag] = i; return i; })()];

  function reply(text, ctx = {}) {
    if (!M) return { tag: 'no_entiendo', conf: 0, text: 'Todavía estoy despertando mi cerebro, dame un segundito.', emotion: 'thinking', low: true };
    const { best, p } = predict(text);
    const real = { tag: M.intents[best].tag, conf: p };
    let it = M.intents[best], low = p < TH_LOW, r, out, via = '';
    if (low) {
      const c = continuation(text);
      if (c) { r = c.r; out = r.t; via = c.key; it = { tag: c.key }; }
      else { it = M.intents.find(x => x.tag === 'no_entiendo') || it; r = pick(it); }
    } else r = pick(it);
    if (out === undefined) {
      const f = mem.facts;
      switch (it.tag) {
        case 'repetir': out = lastReply ? 'Te lo repito. ' + lastReply : 'Todavía no he dicho nada, ¿qué quieres saber?'; break;
        case 'nombre_usuario': { const n = extractName(text); out = n ? r.t : 'No alcancé a oír bien tu nombre. ¿Me lo repites?'; break; }
        case 'mi_nombre': out = f.name ? r.t : 'Todavía no me has dicho tu nombre. ¿Cómo te llamas?'; break;
        case 'que_ves': out = ctx.vision || 'No puedo ver nada ahorita.'; break;
        case 'que_recuerdas': out = memoriaTxt(); break;
        case 'olvidar': mem = fresh(); out = r.t; break;
        case 'que_dije': { const t = mem.turns[mem.turns.length - 1]; out = t ? `Hace un rato me dijiste: ${t.u}.` : 'Todavía no hemos hablado de nada, empecemos.'; break; }
        case 'cuando_cumple': out = f.birthday ? `Tu cumpleaños es ${f.birthday}, no se me olvida.` : 'Todavía no me dices cuándo cumples años. ¿Cuándo es?'; break;
        case 'mi_mascota': out = f.pet ? `Tienes un ${f.pet.type}${f.pet.name ? ' y se llama ' + f.pet.name : ', pero no me has dicho cómo se llama'}.` : 'No me has contado de mascotas. ¿Tienes alguna?'; break;
        case 'que_me_gusta': out = mem.likes.length ? `Me has dicho que te gusta ${join(mem.likes.slice(-5))}.` : 'Todavía no me has dicho qué te gusta. Cuéntame.'; break;
        case 'emocion_ahora': { const lm = lastMood(3); out = lm ? `Por lo que me has contado, creo que te sientes ${lm.m}. ¿Voy bien?` : 'No puedo leer la mente, pero por tu voz creo que estás tranquilo. ¿Cómo te sientes en realidad?'; break; }
        default: out = r.t;
      }
    }
    out = out.replace('{nombre}', mem.facts.name || 'amigo').replace('{hora}', horaTxt()).replace('{fecha}', fechaTxt());
    learn(text, it.tag === 'nombre_usuario' || it.tag === 'recordar_esto' ? it.tag : real.tag);
    if (['saludo', 'buenos_dias', 'despertar', 'te_extrano', 'llegue_casa', 'buenas_noches'].includes(it.tag) && Math.random() < .75) { const rc = recallLine(); if (rc) out += ' ' + rc; }
    const action = /^voz_|^volumen_/.test(it.tag) ? it.tag : '';
    if (it.tag !== 'repetir') lastReply = out;
    prevTag = via ? (EMPATHY.has(prevTag) && via === 'cont_empatia' ? prevTag : (via === 'cont_empatia' ? 'triste_usuario' : prevTag)) : it.tag;
    cap(mem.turns, 40); mem.turns.push({ u: text.slice(0, 160), tag: real.tag, t: Date.now() }); save();
    return { tag: real.tag, conf: real.conf, text: out, emotion: r.e, low, action, via };
  }

  return { load, reply, device, get version() { return M && M.version; }, get info() { return M; }, get memory() { return mem; }, forget() { mem = fresh(); save(); } };
})();
