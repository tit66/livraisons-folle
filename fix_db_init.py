import re

with open("app.py", "r") as f:
    content = f.read()

# Replace the fragile init_connection
old_init = """@st.cache_resource
def init_connection():
    engine = create_engine(DB_URI)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS company_closures (id SERIAL PRIMARY KEY, start_date DATE NOT NULL, end_date DATE NOT NULL, reason VARCHAR(255))"))
        conn.execute(text(\"\"\"
            CREATE TABLE IF NOT EXISTS drivers (
                id SERIAL PRIMARY KEY, first_name VARCHAR(100), last_name VARCHAR(100), email VARCHAR(255), birth_date DATE, phone VARCHAR(50), 
                license_number VARCHAR(100), license_types VARCHAR(255), license_expiry DATE, 
                caces VARCHAR(255), caces_expiry DATE, fimo_fco_expiry DATE, 
                driver_card_number VARCHAR(100), driver_card_expiry DATE,
                license_front_path VARCHAR(500), license_back_path VARCHAR(500), is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\"))
        # S'assurer que les nouvelles colonnes existent (Carte Conducteur)
        try: conn.execute(text("ALTER TABLE drivers ADD COLUMN driver_card_number VARCHAR(100)"))
        except: pass
        try: conn.execute(text("ALTER TABLE drivers ADD COLUMN driver_card_expiry DATE"))
        except: pass

        conn.execute(text(\"\"\"
            CREATE TABLE IF NOT EXISTS vehicles (
                id SERIAL PRIMARY KEY, license_plate VARCHAR(50) UNIQUE, vehicle_type VARCHAR(100), brand_model VARCHAR(150), 
                next_technical_inspection DATE, next_tachograph_inspection DATE, next_speed_limiter_inspection DATE, 
                is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\"))
    return engine"""

new_init = """@st.cache_resource
def init_connection():
    engine = create_engine(DB_URI)
    
    def safe_execute(query):
        try:
            with engine.begin() as conn:
                conn.execute(text(query))
        except Exception as e:
            pass # Ignore expected errors like 'column already exists'

    safe_execute("CREATE TABLE IF NOT EXISTS company_closures (id SERIAL PRIMARY KEY, start_date DATE NOT NULL, end_date DATE NOT NULL, reason VARCHAR(255))")
    
    safe_execute(\"\"\"
        CREATE TABLE IF NOT EXISTS drivers (
            id SERIAL PRIMARY KEY, first_name VARCHAR(100), last_name VARCHAR(100), email VARCHAR(255), birth_date DATE, phone VARCHAR(50), 
            license_number VARCHAR(100), license_types VARCHAR(255), license_expiry DATE, 
            caces VARCHAR(255), caces_expiry DATE, fimo_fco_expiry DATE, 
            driver_card_number VARCHAR(100), driver_card_expiry DATE,
            license_front_path VARCHAR(500), license_back_path VARCHAR(500), is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    \"\"\")
    
    safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_number VARCHAR(100)")
    safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_expiry DATE")
    
    safe_execute(\"\"\"
        CREATE TABLE IF NOT EXISTS vehicles (
            id SERIAL PRIMARY KEY, license_plate VARCHAR(50) UNIQUE, vehicle_type VARCHAR(100), brand_model VARCHAR(150), 
            next_technical_inspection DATE, next_tachograph_inspection DATE, next_speed_limiter_inspection DATE, 
            is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    \"\"\")
    
    return engine"""

if old_init in content:
    content = content.replace(old_init, new_init)
    with open("app.py", "w") as f:
        f.write(content)
    print("Fixed.")
else:
    print("Failed to find init block.")
