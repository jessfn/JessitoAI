#!/usr/bin/env bash
# Despliegue de Blu en el VPS:  cd /var/www/jessito && ./deploy.sh
# Uso: ./deploy.sh [--train]
# git pull -> dependencias -> versión nueva -> reinicio de la API.  Las apps abiertas se actualizan solas (SSE).
set -euo pipefail
cd "$(dirname "$0")"
git pull --ff-only
(cd server && npm install --omit=dev --no-audit --no-fund --silent && chmod -R go+rX .)
if [ -d train/.venv ]; then train/.venv/bin/pip install -q -r train/requirements.txt; fi
# datos semilla -> PostgreSQL (idempotente) y, con --train, re-entrena la red neuronal
if [ -f /etc/jessito.env ] && [ -d train/.venv ]; then
  set -a; . /etc/jessito.env; set +a
  train/.venv/bin/python train/seed.py
  if [ "${1:-}" = "--train" ]; then (cd train && .venv/bin/python brain.py && .venv/bin/python gen.py); fi
fi
python3 - <<'PY'
import json, subprocess, time, os
p = 'public/version.json'
try: cur = json.load(open(p))
except Exception: cur = {}
sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
cur['app'] = sha + '-' + time.strftime('%m%d%H%M')
cur.setdefault('model', '0')
cur['version'] = cur['app'] + '.' + cur['model'] + ('.' + cur['gen'] if cur.get('gen') else '')
json.dump(cur, open(p + '.tmp', 'w')); os.replace(p + '.tmp', p)
print('version', cur['version'])
PY
chown -R www-data:www-data public || true
systemctl restart jessito-api
echo "listo"
