-- Base de datos de Blu (PostgreSQL)
CREATE TABLE IF NOT EXISTS intents (
  id          SERIAL PRIMARY KEY,
  tag         TEXT UNIQUE NOT NULL,
  emotion     TEXT NOT NULL DEFAULT 'neutral',
  description TEXT DEFAULT '',
  created_at  TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS utterances (          -- lo que dice la persona
  id         SERIAL PRIMARY KEY,
  intent_id  INT NOT NULL REFERENCES intents(id) ON DELETE CASCADE,
  text       TEXT NOT NULL,
  source     TEXT NOT NULL DEFAULT 'seed',       -- seed | user | log
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (intent_id, text)
);
CREATE TABLE IF NOT EXISTS responses (           -- lo que contesta Blu
  id         SERIAL PRIMARY KEY,
  intent_id  INT NOT NULL REFERENCES intents(id) ON DELETE CASCADE,
  text       TEXT NOT NULL,
  emotion    TEXT NOT NULL DEFAULT 'neutral',
  source     TEXT NOT NULL DEFAULT 'seed',
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (intent_id, text)
);
CREATE TABLE IF NOT EXISTS conversations (       -- registro de cada turno
  id            BIGSERIAL PRIMARY KEY,
  session       TEXT,
  user_text     TEXT NOT NULL,
  intent        TEXT,
  confidence    REAL,
  reply         TEXT,
  emotion       TEXT,
  vision        JSONB,
  model_version TEXT,
  reviewed      BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS conv_conf_idx ON conversations (reviewed, confidence);
CREATE TABLE IF NOT EXISTS training_runs (
  id          SERIAL PRIMARY KEY,
  started_at  TIMESTAMPTZ DEFAULT now(),
  finished_at TIMESTAMPTZ,
  version     TEXT,
  n_intents   INT,
  n_examples  INT,
  val_acc     REAL,
  train_acc   REAL,
  notes       TEXT
);
CREATE TABLE IF NOT EXISTS memories (            -- recuerdos de cada dispositivo (respaldo de la memoria local)
  device     TEXT PRIMARY KEY,
  data       JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now()
);
