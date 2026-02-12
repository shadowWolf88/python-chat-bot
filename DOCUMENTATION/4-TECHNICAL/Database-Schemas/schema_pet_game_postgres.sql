CREATE TABLE pet (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE,
                name TEXT, species TEXT, gender TEXT,
                hunger INTEGER DEFAULT 70, happiness INTEGER DEFAULT 70,
                energy INTEGER DEFAULT 70, hygiene INTEGER DEFAULT 80,
                coins INTEGER DEFAULT 0, xp INTEGER DEFAULT 0,
                stage TEXT DEFAULT 'Baby', adventure_end REAL DEFAULT 0,
                last_updated REAL, hat TEXT DEFAULT 'None');
-- Username is already unique via table constraint
