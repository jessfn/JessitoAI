// API de Blu: guarda conversaciones en PostgreSQL, avisa por SSE cuando hay versión nueva,
// y permite enseñarle frases nuevas y re-entrenar la red neuronal (con clave de administrador).
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const { spawn } = require('child_process');
const { Pool } = require('pg');

const PORT = +process.env.PORT || 3070;
const ROOT = path.join(__dirname, '..');
const VERSION_FILE = path.join(ROOT, 'public', 'version.json');
const PYTHON = process.env.PYTHON || path.join(ROOT, 'train', '.venv', 'bin', 'python');
const ADMIN_KEY = process.env.ADMIN_KEY || '';
const EMOTIONS = ['neutral', 'happy', 'sad', 'surprised', 'thinking', 'love', 'angry', 'listening', 'sleepy'];
const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 5 });
pool.on('error', e => console.error('pg', e.message));

// ---------- utilidades ----------
const send = (res, code, obj) => { res.writeHead(code, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' }); res.end(JSON.stringify(obj)); };
const readBody = (req, max = 16384) => new Promise((ok, no) => {
  let n = 0, b = [];
  req.on('data', c => { n += c.length; if (n > max) { no(new Error('grande')); req.destroy(); } else b.push(c); });
  req.on('end', () => { try { ok(JSON.parse(Buffer.concat(b).toString() || '{}')); } catch (e) { no(new Error('json')); } });
});
const sha = s => crypto.createHash('sha256').update(String(s)).digest();
const isAdmin = req => ADMIN_KEY && crypto.timingSafeEqual(sha(req.headers['x-admin-key'] || ''), sha(ADMIN_KEY));
const hits = new Map();
function limited(ip, max = 90) {
  const now = Date.now(), h = hits.get(ip) || { n: 0, t: now };
  if (now - h.t > 60000) { h.n = 0; h.t = now; }
  h.n++; hits.set(ip, h); return h.n > max;
}
setInterval(() => { const now = Date.now(); for (const [k, v] of hits) if (now - v.t > 120000) hits.delete(k); }, 60000);
const str = (v, n) => (typeof v === 'string' ? v.trim().slice(0, n) : '');

// ---------- versión / SSE ----------
function readVersion() { try { return JSON.parse(fs.readFileSync(VERSION_FILE, 'utf8')); } catch { return { version: 'dev', app: 'dev', model: '0' }; } }
const clients = new Set();
let last = JSON.stringify(readVersion());
fs.watchFile(VERSION_FILE, { interval: 1500 }, () => {
  const cur = JSON.stringify(readVersion());
  if (cur === last) return;
  last = cur;
  for (const c of clients) c.write(`event: version\ndata: ${cur}\n\n`);
});
setInterval(() => { for (const c of clients) c.write(': ping\n\n'); }, 25000);

// ---------- entrenamiento ----------
const train = { running: false, log: [], started: null, code: null };
function startTrain() {
  if (train.running) return false;
  train.running = true; train.log = []; train.started = Date.now(); train.code = null;
  const push = d => { train.log.push(...d.toString().split('
').filter(Boolean)); train.log = train.log.slice(-120); };
  const steps = ['brain.py', 'gen.py'];                       // 1) clasificador de intención  2) generador de respuestas
  const next = i => {
    if (i >= steps.length) { train.running = false; train.code = 0; return; }
    train.log.push(`== ${steps[i]} ==`);
    const p = spawn(PYTHON, [steps[i]], { cwd: path.join(ROOT, 'train'), env: { ...process.env, PYTHONIOENCODING: 'utf-8' } });
    p.stdout.on('data', push); p.stderr.on('data', push);
    p.on('close', code => { if (code !== 0) { train.running = false; train.code = code; } else next(i + 1); });
    p.on('error', e => { train.running = false; train.code = -1; train.log.push('error: ' + e.message); });
  };
  next(0);
  return true;
}

// ---------- rutas ----------
async function route(req, res) {
  const url = new URL(req.url, 'http://x'), p = url.pathname;
  const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();

  if (p === '/api/health') return send(res, 200, { ok: true });
  if (p === '/api/version') return send(res, 200, readVersion());

  if (p === '/api/events') {
    res.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-store', connection: 'keep-alive', 'x-accel-buffering': 'no' });
    res.write(`event: version\ndata: ${last}\n\n`);
    clients.add(res); req.on('close', () => clients.delete(res)); return;
  }

  if (p === '/api/log' && req.method === 'POST') {
    if (limited(ip)) return send(res, 429, { error: 'demasiadas' });
    const b = await readBody(req);
    const user = str(b.user_text, 300); if (!user) return send(res, 400, { error: 'vacio' });
    let vision = null;
    if (b.vision && typeof b.vision === 'object') { const s = JSON.stringify(b.vision); if (s.length < 600) vision = s; }
    const conf = Number.isFinite(b.confidence) ? Math.max(0, Math.min(1, b.confidence)) : null;
    await pool.query('INSERT INTO conversations(session,user_text,intent,confidence,reply,emotion,vision,model_version) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)',
      [str(b.session, 64), user, str(b.intent, 60), conf, str(b.reply, 500), str(b.emotion, 20), vision, str(b.model_version, 40)]);
    return send(res, 200, { ok: true });
  }

  // ----- recuerdos (respaldo de la memoria del dispositivo) -----
  if (p === '/api/memory') {
    if (limited('m' + ip, 60)) return send(res, 429, { error: 'demasiadas' });
    if (req.method === 'POST') {
      const b = await readBody(req, 12000);
      const dev = str(b.device, 64); if (!/^[a-z0-9]{8,64}$/.test(dev) || !b.memory || typeof b.memory !== 'object') return send(res, 400, { error: 'datos inválidos' });
      const js = JSON.stringify(b.memory); if (js.length > 10000) return send(res, 413, { error: 'grande' });
      await pool.query('INSERT INTO memories(device,data,updated_at) VALUES ($1,$2,now()) ON CONFLICT (device) DO UPDATE SET data=EXCLUDED.data,updated_at=now()', [dev, js]);
      return send(res, 200, { ok: true });
    }
    const dev = str(url.searchParams.get('device'), 64);
    const r = await pool.query('SELECT data FROM memories WHERE device=$1', [dev]);
    return send(res, 200, { memory: r.rows[0] ? r.rows[0].data : null });
  }

  // ----- administración -----
  if (p.startsWith('/api/admin/')) {
    if (limited('adm' + ip, 120) ) return send(res, 429, { error: 'demasiadas' });
    if (!isAdmin(req)) return send(res, 401, { error: 'clave incorrecta' });

    if (p === '/api/admin/summary') {
      const q = t => pool.query(t).then(r => r.rows);
      const [counts, intents, unknown, runs] = await Promise.all([
        q(`SELECT (SELECT count(*) FROM intents) intents,(SELECT count(*) FROM utterances) utterances,
                  (SELECT count(*) FROM responses) responses,(SELECT count(*) FROM conversations) conversations`),
        q(`SELECT i.tag,i.emotion,(SELECT count(*) FROM utterances u WHERE u.intent_id=i.id) n FROM intents i ORDER BY i.tag`),
        q(`SELECT id,user_text,intent,confidence,created_at FROM conversations
           WHERE reviewed=false AND (confidence<0.6 OR intent='no_entiendo') ORDER BY id DESC LIMIT 60`),
        q(`SELECT version,n_examples,val_acc,finished_at FROM training_runs ORDER BY id DESC LIMIT 5`)]);
      return send(res, 200, { counts: counts[0], intents, unknown, runs, version: readVersion(), training: { running: train.running } });
    }
    if (p === '/api/admin/teach' && req.method === 'POST') {
      const b = await readBody(req);
      const text = str(b.text, 300), tag = str(b.tag, 40).toLowerCase(), reply = str(b.reply, 500);
      if (!text || !/^[a-z0-9_]{2,40}$/.test(tag)) return send(res, 400, { error: 'frase o intención inválida' });
      const emo = EMOTIONS.includes(b.emotion) ? b.emotion : null;
      const cl = await pool.connect();
      try {
        await cl.query('BEGIN');
        let r = await cl.query('SELECT id,emotion FROM intents WHERE tag=$1', [tag]);
        if (!r.rowCount) r = await cl.query('INSERT INTO intents(tag,emotion) VALUES ($1,$2) RETURNING id,emotion', [tag, emo || 'neutral']);
        const iid = r.rows[0].id;
        await cl.query("INSERT INTO utterances(intent_id,text,source) VALUES ($1,$2,'user') ON CONFLICT DO NOTHING", [iid, text]);
        if (reply) await cl.query("INSERT INTO responses(intent_id,text,emotion,source) VALUES ($1,$2,$3,'user') ON CONFLICT DO NOTHING", [iid, reply, emo || r.rows[0].emotion]);
        if (b.conv_id) await cl.query('UPDATE conversations SET reviewed=true WHERE id=$1', [b.conv_id | 0]);
        await cl.query('COMMIT');
      } catch (e) { await cl.query('ROLLBACK'); throw e; } finally { cl.release(); }
      return send(res, 200, { ok: true });
    }
    if (p === '/api/admin/dismiss' && req.method === 'POST') {
      const b = await readBody(req);
      await pool.query('UPDATE conversations SET reviewed=true WHERE id=$1', [b.conv_id | 0]);
      return send(res, 200, { ok: true });
    }
    if (p === '/api/admin/train' && req.method === 'POST') return send(res, 200, { started: startTrain() });
    if (p === '/api/admin/train-status') return send(res, 200, { running: train.running, code: train.code, log: train.log, started: train.started });
  }
  send(res, 404, { error: 'no existe' });
}

http.createServer((req, res) => {
  route(req, res).catch(e => { console.error(e.message); if (!res.headersSent) send(res, e.message === 'grande' ? 413 : 500, { error: 'error' }); });
}).listen(PORT, '127.0.0.1', () => console.log('jessito-api en', PORT));
