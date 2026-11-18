#!/usr/bin/env bash
# Despliegue de Blu en el VPS:  cd /var/www/jessito && ./deploy.sh
# git pull -> dependencias -> versión nueva -> reinicio de la API.  Las apps abiertas se actualizan solas (SSE).
set -euo pipefail
cd "$(dirname "$0")"
git pull --ff-only
(cd server && npm install --omit=dev --no-audit --no-fund --silent)
if [ -d train/.venv ]; then train/.venv/bin/pip install -q -r train/requirements.txt; fi
python3 - <<'PY'
import json, subprocess, time, os
p = 'public/version.json'
try: cur = json.load(open(p))
except Exception: cur = {}
sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
cur['app'] = sha + '-' + time.strftime('%m%d%H%M')
cur.setdefault('model', '0')
cur['version'] = cur['app'] + '.' + cur['model']
json.dump(cur, open(p + '.tmp', 'w')); os.replace(p + '.tmp', p)
print('version', cur['version'])
PY
chown -R www-data:www-data public || true
systemctl restart jessito-api
echo "listo"
