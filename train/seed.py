"""Crea las tablas y carga los datos semilla en PostgreSQL.  Uso: DATABASE_URL=... python seed.py"""
import os, sys
import psycopg2
from seed_data import I

here = os.path.dirname(os.path.abspath(__file__))
con = psycopg2.connect(os.environ['DATABASE_URL'])
cur = con.cursor()
cur.execute(open(os.path.join(here, 'schema.sql'), encoding='utf-8').read())
nu = nr = 0
for tag, d in I.items():
    cur.execute("INSERT INTO intents(tag,emotion,description) VALUES (%s,%s,%s) "
                "ON CONFLICT (tag) DO UPDATE SET emotion=EXCLUDED.emotion RETURNING id", (tag, d['emotion'], d['desc']))
    iid = cur.fetchone()[0]
    for u in d['users']:
        cur.execute("INSERT INTO utterances(intent_id,text,source) VALUES (%s,%s,'seed') ON CONFLICT DO NOTHING", (iid, u))
        nu += cur.rowcount
    for r in d['replies']:
        cur.execute("INSERT INTO responses(intent_id,text,emotion,source) VALUES (%s,%s,%s,'seed') ON CONFLICT DO NOTHING",
                    (iid, r, d['emotion']))
        nr += cur.rowcount
con.commit()
print(f'intenciones={len(I)} frases nuevas={nu} respuestas nuevas={nr}')
