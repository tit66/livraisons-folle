from sqlalchemy import create_engine, text

engine = create_engine("postgresql://n8n:supersecret@n8n-local_postgres_1:5432/n8n")

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS catalog_items (
            id SERIAL PRIMARY KEY,
            category VARCHAR(50),
            name VARCHAR(150) UNIQUE
        )
    """))
    conn.execute(text("INSERT INTO catalog_items (category, name) VALUES ('material', 'Sable'), ('material', 'Gravier'), ('material', 'Terre végétale'), ('material', 'Mélange béton') ON CONFLICT DO NOTHING"))
    conn.execute(text("INSERT INTO catalog_items (category, name) VALUES ('waste', 'Gravats'), ('waste', 'DIB (Tout venant)'), ('waste', 'Déchets verts'), ('waste', 'Bois') ON CONFLICT DO NOTHING"))
