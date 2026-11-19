// Visión propia de Jessito (sin APIs): analiza la cámara en el navegador.
// Detecta movimiento, zonas de piel (presencia), posición y cantidad de luz.
// Es un detector sencillo hecho a mano; más adelante lo reemplazamos por una CNN entrenada por nosotros.
const Vision = (() => {
  const W = 48, H = 36;
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  let video = null, prev = null, timer = null;
  const s = { on: false, person: false, personX: .5, personY: .5, area: 0, motion: 0, moveX: .5, moveY: .5, light: .5, lastMotion: 0, lastSeen: 0 };
  const sm = (a, b, k) => a + (b - a) * k;

  function step() {
    if (!video || video.readyState < 2) return;
    cx.drawImage(video, 0, 0, W, H);
    const d = cx.getImageData(0, 0, W, H).data, n = W * H, gray = new Float32Array(n);
    let light = 0, mN = 0, mx = 0, my = 0, sk = 0, sx = 0, sy = 0;
    for (let i = 0; i < n; i++) {
      const r = d[i * 4], g = d[i * 4 + 1], b = d[i * 4 + 2], y = .299 * r + .587 * g + .114 * b;
      gray[i] = y; light += y;
      const x = i % W, yy = (i / W) | 0;
      if (prev && Math.abs(y - prev[i]) > 28) { mN++; mx += x; my += yy; }
      const cb = 128 - .168736 * r - .331264 * g + .5 * b, cr = 128 + .5 * r - .418688 * g - .081312 * b;
      if (y > 45 && cb > 77 && cb < 127 && cr > 133 && cr < 173) { sk++; sx += x; sy += yy; }
    }
    prev = gray; light /= n * 255;
    s.light = sm(s.light, light, .2);
    const mf = mN / n;
    s.motion = sm(s.motion, mf, .4);
    if (mf > .012) { s.moveX = sm(s.moveX, mx / mN / W, .5); s.moveY = sm(s.moveY, my / mN / H, .5); s.lastMotion = Date.now(); }
    const sf = sk / n;
    s.area = sm(s.area, sf, .25);
    if (sf > .035 && s.light > .12) { s.personX = sm(s.personX, sx / sk / W, .35); s.personY = sm(s.personY, sy / sk / H, .35); s.lastSeen = Date.now(); }
    s.person = Date.now() - s.lastSeen < 2500;
  }

  return {
    async start(v) {
      video = v;
      try { v.srcObject = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false }); await v.play().catch(() => {}); s.on = true; }
      catch { s.on = false; v.style.display = 'none'; return false; }
      timer = setInterval(step, 130); return true;
    },
    // hacia dónde mira Jessito: x,y en [-1,1] (espejo, como un espejo), o null si no hay nada que seguir
    get gaze() {
      if (!s.on) return null;
      if (s.person) return { x: (.5 - s.personX) * 2, y: (s.personY - .5) * 1.6 };
      if (Date.now() - s.lastMotion < 2000) return { x: (.5 - s.moveX) * 2, y: (s.moveY - .5) * 1.6 };
      return null;
    },
    get state() { return s; },
    // frase en español de lo que Jessito ve
    summary() {
      if (!s.on) return 'No puedo ver nada porque mi cámara no está encendida. ¿Me das permiso de usarla?';
      if (s.light < .1) return 'Está muy oscuro, casi no veo nada. ¿Puedes prender una luz?';
      if (s.person) {
        const side = s.personX < .38 ? 'hacia el lado derecho de mi vista' : s.personX > .62 ? 'hacia el lado izquierdo de mi vista' : 'justo en el centro';
        const dist = s.area > .16 ? 'muy cerquita' : s.area > .07 ? 'a una buena distancia' : 'un poquito lejos';
        const mv = s.motion > .02 ? ' Y te estás moviendo, ¿verdad?' : ' Estás muy quietecito.';
        return `Te veo. Estás ${side}, ${dist}.${mv}`;
      }
      if (Date.now() - s.lastMotion < 4000) return 'Veo que algo se mueve, pero no distingo bien quién es.';
      return s.light > .6 ? 'Veo un lugar con mucha luz, pero no veo a nadie ahorita.' : 'Veo un lugar tranquilo, pero no veo a nadie ahorita.';
    },
    // resumen para guardar en la base de datos
    snapshot() { return { person: s.person, x: +s.personX.toFixed(2), area: +s.area.toFixed(3), motion: +s.motion.toFixed(3), light: +s.light.toFixed(2) }; }
  };
})();
