from sqlalchemy import create_engine, text

engine = create_engine("postgresql://n8n:supersecret@n8n-local_postgres_1:5432/n8n")
with engine.begin() as conn:
    try:
        conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS driver_id INTEGER"))
        conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS vehicle_id INTEGER"))
        conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS trailer_id INTEGER"))
    except Exception as e:
        print("Error altering orders:", e)

    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vehicle_issues (
                id SERIAL PRIMARY KEY,
                driver_id INTEGER,
                vehicle_id INTEGER,
                description TEXT,
                photo_data TEXT,
                is_resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
    except Exception as e:
        print("Error creating vehicle_issues:", e)
