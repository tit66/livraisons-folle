import streamlit as st
import pandas as pd
import os
import re as regex
import datetime
import requests
import json
import base64
import uuid
from sqlalchemy import create_engine, text
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title='Livraisons Folles', page_icon='🐙', layout='wide')

import os as _os
DB_URI = _os.environ.get('DATABASE_URL', 'postgresql://n8n:supersecret@postgres:5432/n8n')

# ─────────────────────────────────────────────────────────────────────────────
# MULTILINGUE - VUE CHAUFFEUR
# ─────────────────────────────────────────────────────────────────────────────
LANGS = {
    "FR": {
        "my_missions": "Mes missions du jour",
        "delivered": "✅ LIVRÉ",
        "report_issue": "❌ Signaler un problème",
        "send_alert": "🚨 Envoyer l'alerte au bureau",
        "my_vehicles": "🚚 Mes Véhicules",
        "no_mission": "Aucune mission pour aujourd'hui.",
        "assigned_truck": "Camion assigné",
        "assigned_trailer": "Remorque assignée",
        "no_vehicle": "Aucun véhicule assigné aujourd'hui.",
        "issue_type": "Type de problème",
        "issue_desc": "Explication détaillée",
        "client": "Client",
        "address": "Adresse",
        "product": "Type produit",
        "waste": "Type de déchet",
        "quantity": "Quantité",
        "loading_point": "Lieu de chargement",
        "unloading_point": "Lieu de déchargement",
        "slot": "Créneau",
        "phone": "Téléphone client",
        "comment": "Commentaire",
        "container_size": "Taille benne",
        "connect_as": "Se connecter en tant que :",
        "open_maps": "🗺️ Ouvrir dans Google Maps",
    },
    "EN": {
        "my_missions": "My missions today",
        "delivered": "✅ DELIVERED",
        "report_issue": "❌ Report an issue",
        "send_alert": "🚨 Send alert to office",
        "my_vehicles": "🚚 My Vehicles",
        "no_mission": "No missions for today.",
        "assigned_truck": "Assigned truck",
        "assigned_trailer": "Assigned trailer",
        "no_vehicle": "No vehicle assigned today.",
        "issue_type": "Issue type",
        "issue_desc": "Detailed description",
        "client": "Client",
        "address": "Address",
        "product": "Product type",
        "waste": "Waste type",
        "quantity": "Quantity",
        "loading_point": "Loading point",
        "unloading_point": "Unloading point",
        "slot": "Time slot",
        "phone": "Client phone",
        "comment": "Comments",
        "container_size": "Skip size",
        "connect_as": "Connect as:",
        "open_maps": "🗺️ Open in Google Maps",
    },
    "ES": {
        "my_missions": "Mis misiones de hoy",
        "delivered": "✅ ENTREGADO",
        "report_issue": "❌ Reportar un problema",
        "send_alert": "🚨 Enviar alerta a la oficina",
        "my_vehicles": "🚚 Mis Vehículos",
        "no_mission": "Sin misiones para hoy.",
        "assigned_truck": "Camión asignado",
        "assigned_trailer": "Remolque asignado",
        "no_vehicle": "Sin vehículo asignado hoy.",
        "issue_type": "Tipo de problema",
        "issue_desc": "Descripción detallada",
        "client": "Cliente",
        "address": "Dirección",
        "product": "Tipo de producto",
        "waste": "Tipo de residuo",
        "quantity": "Cantidad",
        "loading_point": "Punto de carga",
        "unloading_point": "Punto de descarga",
        "slot": "Franja horaria",
        "phone": "Teléfono cliente",
        "comment": "Comentarios",
        "container_size": "Tamaño contenedor",
        "connect_as": "Conectarse como:",
        "open_maps": "🗺️ Abrir en Google Maps",
    },
    "PT": {
        "my_missions": "Minhas missões de hoje",
        "delivered": "✅ ENTREGUE",
        "report_issue": "❌ Reportar um problema",
        "send_alert": "🚨 Enviar alerta ao escritório",
        "my_vehicles": "🚚 Meus Veículos",
        "no_mission": "Sem missões para hoje.",
        "assigned_truck": "Caminhão atribuído",
        "assigned_trailer": "Reboque atribuído",
        "no_vehicle": "Nenhum veículo atribuído hoje.",
        "issue_type": "Tipo de problema",
        "issue_desc": "Descrição detalhada",
        "client": "Cliente",
        "address": "Endereço",
        "product": "Tipo de produto",
        "waste": "Tipo de resíduo",
        "quantity": "Quantidade",
        "loading_point": "Ponto de carregamento",
        "unloading_point": "Ponto de descarga",
        "slot": "Horário",
        "phone": "Telefone do cliente",
        "comment": "Comentários",
        "container_size": "Tamanho do contêiner",
        "connect_as": "Conectar como:",
        "open_maps": "🗺️ Abrir no Google Maps",
    },
}

def get_lang(nationality):
    if not nationality:
        return LANGS["FR"]
    n = str(nationality).lower()
    if any(x in n for x in ["port", "brésil", "bresil", "brasil"]):
        return LANGS["PT"]
    if any(x in n for x in ["espagn", "mexic", "argentin", "colombi"]):
        return LANGS["ES"]
    if any(x in n for x in ["angl", "brit", "irland", "english", "amér", "amer"]):
        return LANGS["EN"]
    return LANGS["FR"]

# ─────────────────────────────────────────────────────────────────────────────
# INITIALISATION DE LA BASE DE DONNÉES
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def init_connection():
    engine = create_engine(DB_URI)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key VARCHAR(50) PRIMARY KEY,
                value TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS company_closures (
                id SERIAL PRIMARY KEY,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                reason VARCHAR(255)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS drivers (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                license_expiry DATE,
                fimo_fco_expiry DATE,
                caces_expiry DATE,
                is_active BOOLEAN DEFAULT true,
                notes TEXT,
                driver_card_number VARCHAR(100),
                driver_card_expiry DATE,
                nationality VARCHAR(100)
            )
        """))
        conn.execute(text("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_number VARCHAR(100)"))
        conn.execute(text("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_expiry DATE"))
        conn.execute(text("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS nationality VARCHAR(100)"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                brand VARCHAR(100),
                model VARCHAR(100),
                license_plate VARCHAR(50) UNIQUE,
                type VARCHAR(100),
                is_trailer BOOLEAN DEFAULT false,
                control_valid_until DATE,
                tachograph_valid_until DATE,
                speed_limiter_valid_until DATE,
                is_available BOOLEAN DEFAULT true
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                type VARCHAR(50),
                email VARCHAR(255),
                phone VARCHAR(50),
                billing_address TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sites (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id),
                label VARCHAR(255),
                address TEXT,
                gmaps_link TEXT,
                is_active BOOLEAN DEFAULT true
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS catalog_items (
                id SERIAL PRIMARY KEY,
                category VARCHAR(50),
                name VARCHAR(150),
                UNIQUE (category, name)
            )
        """))
        # Try to add unique constraint if it doesn't exist
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'catalog_items_category_name_key'
                ) THEN
                    ALTER TABLE catalog_items ADD CONSTRAINT catalog_items_category_name_key UNIQUE (category, name);
                END IF;
            EXCEPTION WHEN others THEN NULL;
            END $$;
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS skip_inventory (
                size VARCHAR(20) PRIMARY KEY,
                total_count INTEGER DEFAULT 0
            )
        """))
        conn.execute(text("""
            INSERT INTO skip_inventory (size, total_count) VALUES
                ('8m3', 10), ('10m3', 15), ('15m3', 5), ('30m3', 5)
            ON CONFLICT DO NOTHING
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id),
                site_id INTEGER REFERENCES sites(id),
                service_type VARCHAR(100),
                material VARCHAR(255),
                quantity_tons NUMERIC(10,2),
                container_type VARCHAR(50),
                waste_type VARCHAR(255),
                instructions TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                source VARCHAR(50),
                requested_date DATE,
                requested_slot VARCHAR(50),
                driver_id INTEGER REFERENCES drivers(id),
                vehicle_id INTEGER REFERENCES vehicles(id),
                trailer_id INTEGER REFERENCES vehicles(id),
                created_at TIMESTAMP DEFAULT NOW(),
                loading_point VARCHAR(255),
                unloading_point TEXT
            )
        """))
        conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS loading_point VARCHAR(255)"))
        conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS unloading_point TEXT"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vehicle_issues (
                id SERIAL PRIMARY KEY,
                vehicle_id INTEGER REFERENCES vehicles(id),
                driver_id INTEGER REFERENCES drivers(id),
                description TEXT,
                photo_data TEXT,
                is_resolved BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_issues (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(id),
                driver_id INTEGER REFERENCES drivers(id),
                description TEXT,
                photo_data TEXT,
                is_resolved BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sorting_center_bins (
                id SERIAL PRIMARY KEY,
                bin_type VARCHAR(100) UNIQUE NOT NULL,
                container_size VARCHAR(50) DEFAULT '10m3',
                status VARCHAR(50) DEFAULT 'ok',
                notes TEXT DEFAULT ''
            )
        """))
        conn.execute(text("""
            INSERT INTO sorting_center_bins (bin_type, status) VALUES
                ('Bois', 'ok'), ('Placo', 'ok'), ('Carton', 'ok'), ('Fer', 'ok'), ('DIB', 'ok')
            ON CONFLICT DO NOTHING
        """))
        # Seed default service_type catalog entries
        conn.execute(text("""
            INSERT INTO catalog_items (category, name) VALUES
                ('service_type', 'Livraison de matériaux'),
                ('service_type', 'Location de benne')
            ON CONFLICT DO NOTHING
        """))
        conn.commit()
    return engine

engine = init_connection()

# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────────────────────
def run_query(query, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        conn.commit()
        return result

@st.cache_data(ttl=30)
def load_data(query, params=None):
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params or {})

def extract_coords(url):
    if not url:
        return None, None
    match = regex.search(r'@?([0-9.-]+),([0-9.-]+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def auto_report_orders():
    """Reporte automatiquement les commandes non traitées au lendemain."""
    try:
        run_query("""
            UPDATE orders
            SET requested_date = requested_date + INTERVAL '1 day'
            WHERE requested_date < CURRENT_DATE
              AND status NOT IN ('done', 'cancelled')
        """)
    except Exception:
        pass

def est_jour_ouvrable(date_obj):
    if date_obj.weekday() >= 5:
        return False, "⛔ Ce jour est un week-end."
    try:
        df_closures = load_data(
            "SELECT start_date, end_date, reason FROM company_closures WHERE start_date <= :d AND end_date >= :d",
            {"d": date_obj}
        )
        if not df_closures.empty:
            reason = df_closures.iloc[0]['reason'] or "Fermeture entreprise"
            return False, f"⛔ Ce jour est fermé : {reason}"
    except Exception:
        pass
    return True, "✅ Jour ouvrable"

def check_alerts():
    alerts = []
    today = datetime.date.today()
    soon = today + datetime.timedelta(days=30)
    try:
        df_drivers = load_data(
            "SELECT first_name, last_name, license_expiry, fimo_fco_expiry, driver_card_expiry FROM drivers WHERE is_active = true"
        )
        for _, row in df_drivers.iterrows():
            name = f"{row['first_name']} {row['last_name']}"
            if pd.notna(row['fimo_fco_expiry']):
                exp = row['fimo_fco_expiry']
                if hasattr(exp, 'date'):
                    exp = exp.date()
                if exp < today:
                    alerts.append(f"🚨 **FCO expirée** pour {name} (depuis le {exp.strftime('%d/%m/%Y')})")
                elif exp <= soon:
                    alerts.append(f"⚠️ **FCO expire bientôt** pour {name} (le {exp.strftime('%d/%m/%Y')})")
            if pd.notna(row['driver_card_expiry']):
                exp = row['driver_card_expiry']
                if hasattr(exp, 'date'):
                    exp = exp.date()
                if exp < today:
                    alerts.append(f"🚨 **Carte Conducteur expirée** pour {name} (depuis le {exp.strftime('%d/%m/%Y')})")
                elif exp <= soon:
                    alerts.append(f"⚠️ **Carte Conducteur** de {name} expire le {exp.strftime('%d/%m/%Y')}")
    except Exception:
        pass
    try:
        df_veh = load_data(
            "SELECT license_plate, tachograph_valid_until, speed_limiter_valid_until FROM vehicles WHERE is_available = true"
        )
        for _, row in df_veh.iterrows():
            plate = row['license_plate']
            if pd.notna(row['tachograph_valid_until']):
                exp = row['tachograph_valid_until']
                if hasattr(exp, 'date'):
                    exp = exp.date()
                if exp < today:
                    alerts.append(f"🚚 **Chronotachygraphe** du véhicule {plate} expiré (depuis le {exp.strftime('%d/%m/%Y')})")
                elif exp <= soon:
                    alerts.append(f"⚠️ **Chronotachygraphe** du véhicule {plate} expire le {exp.strftime('%d/%m/%Y')}")
            if pd.notna(row['speed_limiter_valid_until']):
                exp = row['speed_limiter_valid_until']
                if hasattr(exp, 'date'):
                    exp = exp.date()
                if exp < today:
                    alerts.append(f"⚠️ **Limiteur de vitesse** du véhicule {plate} expiré (depuis le {exp.strftime('%d/%m/%Y')})")
                elif exp <= soon:
                    alerts.append(f"⚠️ **Limiteur de vitesse** du véhicule {plate} expire le {exp.strftime('%d/%m/%Y')}")
    except Exception:
        pass
    return alerts

# Créneaux horaires standardisés
SLOTS = ["Indifférent dans la journée", "8h Premier tour", "8h-10h", "10h-12h", "13h-15h", "15h-17h"]

# ─────────────────────────────────────────────────────────────────────────────
# AUTO-REPORT AU DÉMARRAGE
# ─────────────────────────────────────────────────────────────────────────────
auto_report_orders()

# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTIFICATION
# ─────────────────────────────────────────────────────────────────────────────
import hashlib as _hashlib

def _hash_pw(pw: str) -> str:
    return _hashlib.sha256(pw.encode()).hexdigest()

def _check_pw(pw: str, stored: str) -> bool:
    return _hash_pw(pw) == stored

# Initialiser session
if "auth_role" not in st.session_state:
    st.session_state.auth_role = None   # "admin" | "driver"
if "auth_driver_id" not in st.session_state:
    st.session_state.auth_driver_id = None
if "auth_name" not in st.session_state:
    st.session_state.auth_name = None

def show_login():
    st.markdown("""
    <style>
    .login-box { max-width: 420px; margin: 4rem auto; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("### 🔐 Connexion — Livraisons Folles")
    with st.form("main_login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter", type="primary", use_container_width=True)
        if submitted:
            if not email or not password:
                st.error("Email et mot de passe requis.")
            else:
                authenticated = False
                # ── Vérifier admin ──
                try:
                    df_settings = load_data("SELECT key, value FROM system_settings WHERE key IN ('admin_email', 'admin_password_hash')")
                    settings = dict(zip(df_settings["key"], df_settings["value"]))
                    if (email.lower() == settings.get("admin_email", "").lower()
                            and _check_pw(password, settings.get("admin_password_hash", ""))):
                        st.session_state.auth_role = "admin"
                        st.session_state.auth_name = "Admin"
                        authenticated = True
                except Exception:
                    pass
                # ── Vérifier chauffeur ──
                if not authenticated:
                    try:
                        df_drv = load_data(
                            "SELECT id, first_name, last_name, password_hash FROM drivers WHERE LOWER(email)=LOWER(:email) AND is_active=true",
                            {"email": email}
                        )
                        if not df_drv.empty:
                            r = df_drv.iloc[0]
                            if r["password_hash"] and _check_pw(password, r["password_hash"]):
                                st.session_state.auth_role = "driver"
                                st.session_state.auth_driver_id = r["id"]
                                st.session_state.auth_name = f"{r['first_name']} {r['last_name']}"
                                authenticated = True
                    except Exception:
                        pass
                if not authenticated:
                    st.error("Email ou mot de passe incorrect.")
                else:
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Vérifier si connecté ──
if not st.session_state.auth_role:
    show_login()
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🐙 Livraisons Folles")
    st.markdown("---")
    st.write(f"👤 **{st.session_state.auth_name}**")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.auth_role = None
        st.session_state.auth_driver_id = None
        st.session_state.auth_name = None
        st.rerun()
    st.markdown("---")
    if st.session_state.auth_role == "admin":
        navigation = st.sidebar.radio(
            "Navigation",
            [
                "📊 Tableau de bord - Livraisons",
                "➕ Prise de Commande",
                "📅 Planning & Assignation",
                "📍 Suivi du Parc de Bennes",
                "👥 Gestion des Chauffeurs",
                "🚚 Gestion de la Flotte",
                "📱 Vue Chauffeur (Mobile)",
                "♻️ Centre de Tri",
                "⚙️ Paramètres de l'Entreprise",
            ]
        )
    else:
        navigation = "📱 Vue Chauffeur (Mobile)"
        st.info("🚚 Vue Chauffeur")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: TABLEAU DE BORD
# ─────────────────────────────────────────────────────────────────────────────
if navigation == "📊 Tableau de bord - Livraisons":
    st.title("📊 Tableau de bord - Livraisons")
    today = datetime.date.today()

    # 1a. Métriques en haut
    try:
        df_metrics = load_data("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status='done') as done_count,
                COUNT(*) FILTER (WHERE status='pending') as pending_count,
                COUNT(*) FILTER (WHERE status IN ('planned','dispatched')) as planned_count
            FROM orders
            WHERE requested_date = :d
        """, {"d": today})
        df_issues_count = load_data("""
            SELECT COUNT(*) as cnt FROM order_issues WHERE is_resolved = false
        """)
        m = df_metrics.iloc[0] if not df_metrics.empty else None
        issues_cnt = int(df_issues_count.iloc[0]['cnt']) if not df_issues_count.empty else 0

        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        col_m1.metric("📦 Total du jour", int(m['total']) if m is not None else 0)
        col_m2.metric("✅ Terminées", int(m['done_count']) if m is not None else 0)
        col_m3.metric("🕐 En attente", int(m['pending_count']) if m is not None else 0)
        col_m4.metric("📋 Planifiées", int(m['planned_count']) if m is not None else 0)
        col_m5.metric("🚨 Problèmes ouverts", issues_cnt)
    except Exception as e:
        st.error(f"Erreur métriques : {e}")

    st.markdown("---")
    date_filtre = st.date_input("Afficher les livraisons du :", value=today, format="DD/MM/YYYY")

    # 1b. Grand tableau modifiable avec expanders
    try:
        df_orders = load_data("""
            SELECT o.id, c.name as client_name, o.status,
                   o.service_type, o.material, o.waste_type,
                   o.quantity_tons, o.requested_date, o.requested_slot,
                   o.driver_id, o.loading_point, o.unloading_point,
                   CONCAT(d.first_name, ' ', d.last_name) as chauffeur,
                   v.license_plate as vehicule,
                   s.address as adresse,
                   o.instructions,
                   o.container_type
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN drivers d ON o.driver_id = d.id
            LEFT JOIN vehicles v ON o.vehicle_id = v.id
            LEFT JOIN sites s ON o.site_id = s.id
            WHERE o.requested_date = :d
            ORDER BY o.id
        """, {"d": date_filtre})

        # Récupérer les IDs des commandes avec problème non résolu
        df_issues_ids = load_data("""
            SELECT DISTINCT order_id FROM order_issues WHERE is_resolved = false
        """)
        issue_order_ids = set(df_issues_ids['order_id'].tolist()) if not df_issues_ids.empty else set()

        # Chauffeurs actifs pour les selectboxes
        df_drivers_sel = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true ORDER BY first_name")
        drv_dict = {None: "--- Non assigné ---"}
        for _, r in df_drivers_sel.iterrows():
            drv_dict[r['id']] = f"{r['first_name']} {r['last_name']}"

        # Points de chargement / déchargement
        df_loading_pts = load_data("SELECT name FROM catalog_items WHERE category='loading_point' ORDER BY name")
        df_unloading_pts = load_data("SELECT name FROM catalog_items WHERE category='unloading_point' ORDER BY name")
        loading_options = df_loading_pts['name'].tolist() if not df_loading_pts.empty else []
        unloading_options = df_unloading_pts['name'].tolist() if not df_unloading_pts.empty else []

        if df_orders.empty:
            st.info("Aucune livraison pour cette date.")
        else:
            for _, row in df_orders.iterrows():
                order_id = row['id']
                has_issue = order_id in issue_order_ids
                req_date = row['requested_date']
                if hasattr(req_date, 'date'):
                    req_date = req_date.date()

                # Couleur du label
                if has_issue:
                    color_badge = "🔴🚨"
                    color_style = "color: red; font-weight: bold;"
                elif req_date is not None and req_date < today and row['status'] not in ('done', 'cancelled'):
                    color_badge = "🟠"
                    color_style = "color: orange; font-weight: bold;"
                else:
                    color_badge = "⬜"
                    color_style = ""

                details = row['material'] or row['waste_type'] or ""
                expander_label = (
                    f"{color_badge} {row['client_name']} — "
                    f"{row['service_type']} — {details} "
                    f"({req_date.strftime('%d/%m/%Y') if req_date else '?'} / {row['requested_slot'] or '?'}) "
                    f"— {row['chauffeur'] or 'Non assigné'}"
                )

                with st.expander(expander_label):
                    if has_issue:
                        st.error("🚨 Cette commande a un problème non résolu !")

                    fc1, fc2 = st.columns(2)
                    with fc1:
                        new_date = st.date_input(
                            "📅 Date souhaitée",
                            value=req_date if req_date else today,
                            key=f"date_{order_id}",
                            format="DD/MM/YYYY"
                        )
                        slot_idx = SLOTS.index(row['requested_slot']) if row['requested_slot'] in SLOTS else 0
                        new_slot = st.selectbox("⏰ Créneau", SLOTS, index=slot_idx, key=f"slot_{order_id}")
                        # Détection type pour champs fc1
                        stype_edit = str(row['service_type'] or "").lower()
                        is_benne_edit = any(x in stype_edit for x in [
                            "benne", "pose", "retrait", "rotation", "enlèvement", "enlevement", "déplacement"
                        ])
                        if is_benne_edit:
                            df_inv_e = load_data("SELECT size FROM skip_inventory ORDER BY size")
                            inv_e_opts = df_inv_e['size'].tolist() if not df_inv_e.empty else []
                            curr_cont = str(row['container_type'] or "")
                            if inv_e_opts:
                                cont_idx = inv_e_opts.index(curr_cont) if curr_cont in inv_e_opts else 0
                                new_container = st.selectbox("📦 Taille de benne", inv_e_opts, index=cont_idx, key=f"cont_{order_id}")
                            else:
                                new_container = st.text_input("📦 Taille de benne", value=curr_cont, key=f"cont_{order_id}")
                            new_qty = float(row['quantity_tons'] or 0)
                        else:
                            new_container = str(row['container_type'] or "")
                            new_qty = st.number_input("⚖️ Quantité (tonnes)", value=float(row['quantity_tons'] or 0), min_value=0.0, step=0.5, key=f"qty_{order_id}")
                    with fc2:
                        # Material ou waste_type selon service_type
                        if is_benne_edit:
                            new_material = None
                            df_waste_opts = load_data("SELECT name FROM catalog_items WHERE category='waste' ORDER BY name")
                            waste_opts = df_waste_opts['name'].tolist() if not df_waste_opts.empty else []
                            curr_waste = row['waste_type'] or ""
                            if waste_opts:
                                waste_idx = waste_opts.index(curr_waste) if curr_waste in waste_opts else 0
                                new_waste = st.selectbox("🗑️ Type de déchet", waste_opts, index=waste_idx, key=f"waste_{order_id}")
                            else:
                                new_waste = st.text_input("🗑️ Type de déchet", value=curr_waste, key=f"waste_{order_id}")
                            # Point de déchargement
                            df_unload_opts2 = load_data("SELECT name FROM catalog_items WHERE category='unloading_point' ORDER BY name")
                            unload_list = df_unload_opts2['name'].tolist() if not df_unload_opts2.empty else []
                            unload_val = row['unloading_point'] or ""
                            if unload_val and unload_val not in unload_list:
                                unload_list = [unload_val] + unload_list
                            unload_idx = unload_list.index(unload_val) if unload_val in unload_list else 0
                            if unload_list:
                                new_unload = st.selectbox("📍 Point de déchargement", unload_list, index=unload_idx, key=f"unload_{order_id}")
                            else:
                                new_unload = st.text_input("📍 Point de déchargement", value=unload_val, key=f"unload_{order_id}")
                            new_load = row['loading_point'] or ""
                        else:
                            new_waste = None
                            df_mat_opts = load_data("SELECT name FROM catalog_items WHERE category='material' ORDER BY name")
                            mat_opts = df_mat_opts['name'].tolist() if not df_mat_opts.empty else []
                            if "Big Bag" not in mat_opts:
                                mat_opts = mat_opts + ["Big Bag"]
                            curr_mat = row['material'] or ""
                            if mat_opts:
                                mat_idx = mat_opts.index(curr_mat) if curr_mat in mat_opts else 0
                                new_material = st.selectbox("📦 Matériau", mat_opts, index=mat_idx, key=f"mat_{order_id}")
                            else:
                                new_material = st.text_input("📦 Matériau", value=curr_mat, key=f"mat_{order_id}")
                            # Point de chargement
                            df_load_opts2 = load_data("SELECT name FROM catalog_items WHERE category='loading_point' ORDER BY name")
                            load_list = df_load_opts2['name'].tolist() if not df_load_opts2.empty else []
                            load_val = row['loading_point'] or ""
                            if load_val and load_val not in load_list:
                                load_list = [load_val] + load_list
                            load_idx = load_list.index(load_val) if load_val in load_list else 0
                            if load_list:
                                new_load = st.selectbox("📍 Lieu de chargement", load_list, index=load_idx, key=f"load_{order_id}")
                            else:
                                new_load = st.text_input("📍 Lieu de chargement", value=load_val, key=f"load_{order_id}")
                            new_unload = row['unloading_point'] or ""

                        drv_keys = list(drv_dict.keys())
                        curr_drv = row['driver_id'] if row['driver_id'] in drv_keys else None
                        drv_idx = drv_keys.index(curr_drv) if curr_drv in drv_keys else 0
                        new_driver = st.selectbox("👤 Chauffeur", drv_keys, format_func=lambda x: drv_dict[x], index=drv_idx, key=f"drv_{order_id}")

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("💾 Mettre à jour", key=f"upd_{order_id}", type="primary"):
                            run_query("""
                                UPDATE orders SET
                                    requested_date=:rd, requested_slot=:rs, quantity_tons=:qty,
                                    material=:mat, waste_type=:waste, driver_id=:did,
                                    loading_point=:lp, unloading_point=:up,
                                    container_type=:ct
                                WHERE id=:id
                            """, {
                                "rd": new_date, "rs": new_slot, "qty": new_qty,
                                "mat": new_material, "waste": new_waste, "did": new_driver,
                                "lp": new_load, "up": new_unload, "ct": new_container, "id": order_id
                            })
                            st.success("✅ Commande mise à jour.")
                            st.cache_data.clear()
                            st.rerun()
                    with col_btn2:
                        confirm_del = st.checkbox("Confirmer la suppression", key=f"del_confirm_{order_id}")
                        if confirm_del:
                            if st.button("🗑️ Supprimer définitivement", key=f"del_{order_id}", type="secondary"):
                                run_query("DELETE FROM order_issues WHERE order_id=:id", {"id": order_id})
                                run_query("DELETE FROM orders WHERE id=:id", {"id": order_id})
                                st.warning("Commande supprimée.")
                                st.cache_data.clear()
                                st.rerun()
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")

    st.markdown("---")
    st.write("### ⚠️ Rappels & Échéances (Chauffeurs & Flotte)")
    alerts = check_alerts()
    if alerts:
        for a in alerts:
            st.warning(a)
    else:
        st.success("✅ Aucune échéance urgente.")

    st.markdown("---")
    st.write("### 🚨 Signalements Problèmes Véhicules")
    try:
        df_vi = load_data("""
            SELECT vi.id, v.license_plate, vi.description, vi.created_at,
                   CONCAT(d.first_name, ' ', d.last_name) as chauffeur,
                   vi.photo_data
            FROM vehicle_issues vi
            LEFT JOIN vehicles v ON vi.vehicle_id = v.id
            LEFT JOIN drivers d ON vi.driver_id = d.id
            WHERE vi.is_resolved = false
            ORDER BY vi.created_at DESC
        """)
        if df_vi.empty:
            st.success("✅ Aucun problème véhicule non résolu.")
        else:
            for _, row in df_vi.iterrows():
                with st.expander(f"🚨 {row['license_plate']} — {str(row['description'])[:60]}..."):
                    st.write(f"**Signalé par :** {row['chauffeur']}")
                    st.write(f"**Le :** {row['created_at']}")
                    st.write(f"**Description :** {row['description']}")
                    if pd.notna(row['photo_data']) and str(row['photo_data']).strip():
                        photo_val = str(row['photo_data'])
                        if photo_val.startswith("uploads/") and os.path.exists(photo_val):
                            st.image(photo_val, caption="Photo du problème", width=300)
                        elif not photo_val.startswith("uploads/"):
                            try:
                                st.image(base64.b64decode(photo_val), caption="Photo du problème", width=300)
                            except Exception:
                                pass
                    if st.button("✅ Marquer comme Résolu", key=f"resolve_vi_{row['id']}"):
                        run_query("UPDATE vehicle_issues SET is_resolved = true WHERE id = :id", {"id": row['id']})
                        st.success("Résolu !")
                        st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")

    st.markdown("---")
    st.write("### 🚨 Problèmes signalés sur chantier")
    try:
        df_oi = load_data("""
            SELECT oi.id, oi.description, oi.created_at, o.id as order_id,
                   c.name as client, s.address,
                   CONCAT(d.first_name, ' ', d.last_name) as chauffeur,
                   oi.photo_data
            FROM order_issues oi
            LEFT JOIN orders o ON oi.order_id = o.id
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN sites s ON o.site_id = s.id
            LEFT JOIN drivers d ON oi.driver_id = d.id
            WHERE oi.is_resolved = false
            ORDER BY oi.created_at DESC
        """)
        if df_oi.empty:
            st.success("✅ Aucun problème chantier non résolu.")
        else:
            for _, row in df_oi.iterrows():
                with st.expander(f"🚨 {row['client']} — {str(row['description'])[:60]}"):
                    st.write(f"**Chauffeur :** {row['chauffeur']}")
                    st.write(f"**Adresse :** {row['address']}")
                    st.write(f"**Le :** {row['created_at']}")
                    st.write(f"**Description :** {row['description']}")
                    if pd.notna(row['photo_data']) and str(row['photo_data']).strip():
                        photo_val = str(row['photo_data'])
                        if photo_val.startswith("uploads/") and os.path.exists(photo_val):
                            st.image(photo_val, caption="Preuve (Photo)", width=300)
                        elif not photo_val.startswith("uploads/"):
                            try:
                                st.image(base64.b64decode(photo_val), caption="Preuve (Photo)", width=300)
                            except Exception:
                                pass
                    col_oi1, col_oi2 = st.columns(2)
                    with col_oi1:
                        if st.button("🔄 Traiter et Replanifier (Remettre 'En Attente')", key=f"replan_oi_{row['id']}"):
                            run_query("UPDATE orders SET status='pending' WHERE id = :id", {"id": row['order_id']})
                            run_query("UPDATE order_issues SET is_resolved = true WHERE id = :id", {"id": row['id']})
                            st.success("Commande remise en attente.")
                            st.rerun()
                    with col_oi2:
                        if st.button("❌ Annuler définitivement la commande", key=f"cancel_oi_{row['id']}"):
                            run_query("UPDATE orders SET status='cancelled' WHERE id = :id", {"id": row['order_id']})
                            run_query("UPDATE order_issues SET is_resolved = true WHERE id = :id", {"id": row['id']})
                            st.warning("Commande annulée.")
                            st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PRISE DE COMMANDE
# ─────────────────────────────────────────────────────────────────────────────
elif navigation == "➕ Prise de Commande":
    st.title("➕ Prise de Commande")

    df_clients = load_data("SELECT id, name FROM clients ORDER BY name")

    client_dict = {"NEW_CLIENT": "➕ NOUVEAU CLIENT PRO OU PARTICULIER"}
    for _, row in df_clients.iterrows():
        client_dict[row['id']] = row['name']

    selected_client_id = st.selectbox(
        "1️⃣ Client",
        options=[None] + list(client_dict.keys()),
        format_func=lambda x: "--- Choisir un client ---" if x is None else client_dict[x]
    )

    new_c_name = new_c_type = new_c_email = new_c_phone = new_c_address = ""
    new_s_label = new_s_address = new_s_gmaps = ""
    selected_site_id = None
    new_site_label = new_site_address = new_site_gmaps = ""

    # 2a. Type de prestation depuis catalog_items
    df_stype = load_data("SELECT name FROM catalog_items WHERE category='service_type' ORDER BY name")
    service_options = df_stype['name'].tolist() if not df_stype.empty else ["Livraison de matériaux", "Location de benne"]

    if selected_client_id == "NEW_CLIENT":
        st.info("Renseignez les informations de facturation du nouveau client.")
        c_nc1, c_nc2 = st.columns(2)
        with c_nc1:
            new_c_name = st.text_input("Nom / Raison Sociale *")
            new_c_type = st.radio("Type", ["Professionnel", "Particulier"], horizontal=True)
            new_c_email = st.text_input("Email (Pour la facturation)")
        with c_nc2:
            new_c_phone = st.text_input("Téléphone")
            new_c_address = st.text_area("Adresse de facturation")

        st.divider()
        st.write("### 📍 Adresse de la 1ère Livraison")
        c_sa1, c_sa2 = st.columns(2)
        with c_sa1:
            new_s_label = st.text_input("Nom du Chantier (Optionnel, Ex: Chantier Maison Dupont)")
            new_s_address = st.text_area("Adresse de la livraison (Si différente de la facturation)")
        with c_sa2:
            new_s_gmaps = st.text_input("Lien Google Maps (Recommandé pour les chauffeurs)")
            st.caption("Allez sur Google Maps, placez un repère, cliquez sur 'Partager' puis 'Copier le lien'.")

        st.divider()
        prestation = st.radio("3️⃣ Type de Prestation", service_options, horizontal=True)

    elif selected_client_id is not None:
        df_sites = load_data(
            "SELECT id, label, address, gmaps_link FROM sites WHERE client_id = :cid AND is_active = true",
            {"cid": selected_client_id}
        )
        site_dict = {"NEW": "➕ Créer une nouvelle adresse/chantier", "BILLING": "--- Adresse de facturation du client ---"}
        for _, row in df_sites.iterrows():
            site_dict[row['id']] = f"{row['label']} — {row['address']}"

        selected_site_id = st.selectbox(
            "2️⃣ Chantier / Adresse de livraison",
            options=[None] + list(site_dict.keys()),
            format_func=lambda x: "--- Choisir un chantier ---" if x is None else site_dict.get(x, str(x))
        )

        if selected_site_id == "NEW":
            c_ns1, c_ns2 = st.columns(2)
            with c_ns1:
                new_site_label = st.text_input("Nom du chantier (optionnel)")
                new_site_address = st.text_area("Adresse exacte *")
            with c_ns2:
                new_site_gmaps = st.text_input("Lien Google Maps")
                st.caption("Allez sur Google Maps, placez un repère, cliquez sur 'Partager' puis 'Copier le lien'.")

        st.divider()
        prestation = st.radio("3️⃣ Type de Prestation", service_options, horizontal=True)
    else:
        prestation = None

    # Variables commandes
    marchandise = volume_benne = type_benne = action_benne = quantite = None
    instructions = ""
    date_livraison = datetime.date.today()
    creneau_choisi = SLOTS[0]
    loading_point_val = ""
    unloading_point_val = ""

    if prestation is not None:
        st.divider()
        # Détecter si c'est une prestation benne
        is_benne = "benne" in str(prestation).lower()

        if not is_benne:
            # Livraison de matériaux
            df_mat = load_data("SELECT name FROM catalog_items WHERE category='material' ORDER BY name")
            mat_options = df_mat['name'].tolist() if not df_mat.empty else []
            mat_options_display = mat_options + ["Big Bag"]
            marchandise = st.selectbox("Matériau", mat_options_display)
            if marchandise == "Big Bag":
                st.warning("⚠️ **Avertissement de tarification :** La livraison en Big Bag se fait en camion grue. Tarification spécifique applicable.")
            quantite = st.number_input("Quantité (tonnes)", min_value=0.0, step=0.5, value=1.0)

            # 2b. Lieu de chargement
            df_load_pts = load_data("SELECT name FROM catalog_items WHERE category='loading_point' ORDER BY name")
            load_options = df_load_pts['name'].tolist() if not df_load_pts.empty else []
            if load_options:
                loading_point_val = st.selectbox("📍 Lieu de chargement", load_options)
            else:
                loading_point_val = st.text_input("📍 Lieu de chargement")

        else:
            # Location de benne
            action_benne = st.radio("Action", ["Pose", "Rotation", "Enlèvement", "Déplacement"], horizontal=True)
            df_waste = load_data("SELECT name FROM catalog_items WHERE category='waste' ORDER BY name")
            waste_options = df_waste['name'].tolist() if not df_waste.empty else []
            type_benne = st.selectbox("Type de déchets", waste_options) if waste_options else st.text_input("Type de déchets")
            df_inv = load_data("SELECT size FROM skip_inventory ORDER BY size")
            inv_options = df_inv['size'].tolist() if not df_inv.empty else []
            volume_benne = st.selectbox("Volume de benne", inv_options) if inv_options else st.text_input("Volume de benne")
            if type_benne and "gravat" in str(type_benne).lower():
                st.warning("⚠️ Pour les gravats, le volume maximum conseillé est de 10m3")

            # 2b. Point de déchargement
            df_unload_pts = load_data("SELECT name FROM catalog_items WHERE category='unloading_point' ORDER BY name")
            unload_options = df_unload_pts['name'].tolist() if not df_unload_pts.empty else []
            if unload_options:
                unloading_point_val = st.selectbox("📍 Point de déchargement", unload_options)
            else:
                unloading_point_val = st.text_input("📍 Point de déchargement")

        st.divider()
        # 2d. Format DD/MM/YYYY
        date_livraison = st.date_input("📅 Date souhaitée", value=datetime.date.today() + datetime.timedelta(days=1), format="DD/MM/YYYY")
        est_valide, msg_valide = est_jour_ouvrable(date_livraison)
        if not est_valide:
            st.error(msg_valide)
        else:
            st.success(msg_valide)

        # 2c. Créneaux standardisés
        creneau_choisi = st.selectbox("⏰ Créneau", SLOTS)
        instructions = st.text_area("Instructions particulières (Accès, contact sur place...)")

        st.divider()
        if st.button("✅ Valider et Enregistrer", type="primary", use_container_width=True, disabled=not est_valide):
            try:
                final_client_id = selected_client_id
                final_site_id = None

                if selected_client_id == "NEW_CLIENT":
                    if not new_c_name:
                        st.error("Le Nom du client est obligatoire.")
                        st.stop()
                    res_c = run_query("""
                        INSERT INTO clients (name, type, email, phone, billing_address)
                        VALUES (:n, :t, :e, :p, :a) RETURNING id
                    """, {"n": new_c_name, "t": new_c_type, "e": new_c_email, "p": new_c_phone, "a": new_c_address}).fetchone()
                    final_client_id = res_c[0]
                    st.success(f"👤 Nouveau client {new_c_name} créé !")
                    addr_site = new_s_address if new_s_address else new_c_address
                    lbl_site = new_s_label if new_s_label else "Adresse principale"
                    res_s = run_query("""
                        INSERT INTO sites (client_id, label, address, gmaps_link, is_active)
                        VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id
                    """, {"cid": final_client_id, "lbl": lbl_site, "addr": addr_site, "gmaps": new_s_gmaps}).fetchone()
                    final_site_id = res_s[0]

                elif selected_site_id == "NEW":
                    if not new_site_address:
                        st.error("L'adresse du chantier est obligatoire.")
                        st.stop()
                    lbl = new_site_label if new_site_label else "Nouvelle Adresse"
                    res = run_query("""
                        INSERT INTO sites (client_id, label, address, gmaps_link, is_active)
                        VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id
                    """, {"cid": final_client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps}).fetchone()
                    final_site_id = res[0]
                    st.success("📍 Nouveau chantier sauvegardé.")
                else:
                    final_site_id = selected_site_id if selected_site_id not in ("BILLING", None) else None

                service_final = f"Benne - {action_benne}" if is_benne else prestation
                run_query("""
                    INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons,
                        container_type, waste_type, instructions, status, source, requested_date,
                        requested_slot, loading_point, unloading_point)
                    VALUES (:client_id, :site_id, :service_type, :material, :quantity,
                        :container_type, :waste_type, :instructions, 'pending', 'admin_streamlit',
                        :req_date, :req_slot, :lp, :up)
                """, {
                    "client_id": final_client_id, "site_id": final_site_id, "service_type": service_final,
                    "material": marchandise, "quantity": quantite, "container_type": volume_benne,
                    "waste_type": type_benne, "instructions": instructions,
                    "req_date": date_livraison, "req_slot": creneau_choisi,
                    "lp": loading_point_val, "up": unloading_point_val
                })
                st.success(f"🎉 Commande enregistrée pour le {date_livraison.strftime('%d/%m/%Y')} (Créneau : {creneau_choisi}).")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Erreur SQL globale : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PLANNING & ASSIGNATION
# ─────────────────────────────────────────────────────────────────────────────
elif navigation == "📅 Planning & Assignation":
    st.title("📅 Planning & Assignation")
    import time

    # 3a. Format DD/MM/YYYY
    date_planning = st.date_input("Date du planning à préparer", value=datetime.date.today(), format="DD/MM/YYYY")

    with st.expander("🧠 Assistant de Pré-assignation par I.A."):
        api_key = st.text_input("Clé API OpenAI / Gemini", type="password")
        if st.button("✨ Lancer l'optimisation des tournées"):
            try:
                df_pending = load_data("""
                    SELECT o.id, c.name as client, s.address, o.service_type
                    FROM orders o
                    LEFT JOIN clients c ON o.client_id = c.id
                    LEFT JOIN sites s ON o.site_id = s.id
                    WHERE o.requested_date = :d AND o.status = 'pending'
                """, {"d": date_planning})
                df_drivers_ai = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true")
                df_vehicles_ai = load_data("SELECT id, license_plate, type FROM vehicles WHERE is_available = true AND is_trailer = false")

                if df_pending.empty:
                    st.warning("Aucune commande en attente pour cette date.")
                else:
                    with st.spinner("L'I.A. réfléchit à la meilleure répartition..."):
                        if not api_key:
                            drivers_ids = df_drivers_ai['id'].tolist()
                            vehicles_ids = df_vehicles_ai['id'].tolist()
                            count = 0
                            for i, row in df_pending.iterrows():
                                did = drivers_ids[i % len(drivers_ids)] if drivers_ids else None
                                vid = vehicles_ids[i % len(vehicles_ids)] if vehicles_ids else None
                                run_query(
                                    "UPDATE orders SET status='planned', driver_id=:did, vehicle_id=:vid WHERE id=:oid",
                                    {"did": did, "vid": vid, "oid": row['id']}
                                )
                                count += 1
                            st.success(f"✅ {count} commandes ont été assignées. (Mode Prototype)")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        else:
                            prompt = (
                                f"Commandes : {df_pending.to_dict(orient='records')}\n"
                                f"Chauffeurs : {df_drivers_ai.to_dict(orient='records')}\n"
                                f"Camions : {df_vehicles_ai.to_dict(orient='records')}\n"
                                "Règle : Répartis la charge équitablement. Retourne uniquement un tableau JSON."
                            )
                            prompt_system = "Tu es un dispatcheur logistique expert. Retourne UNIQUEMENT un tableau JSON valide, sans Markdown."
                            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                            data = {
                                "model": "gpt-4o-mini",
                                "messages": [
                                    {"role": "system", "content": prompt_system},
                                    {"role": "user", "content": prompt + "\nFormat JSON : [{\"order_id\": 1, \"driver_id\": 2, \"vehicle_id\": 3}]"}
                                ],
                                "temperature": 0.1
                            }
                            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
                            if response.status_code == 200:
                                ai_text = response.json()["choices"][0]["message"]["content"].strip()
                                if ai_text.startswith("```json"):
                                    ai_text = ai_text[7:-3].strip()
                                elif ai_text.startswith("```"):
                                    ai_text = ai_text[3:-3].strip()
                                assignments = json.loads(ai_text)
                                count = 0
                                for a in assignments:
                                    if "order_id" in a and "driver_id" in a and "vehicle_id" in a:
                                        run_query(
                                            "UPDATE orders SET status='planned', driver_id=:did, vehicle_id=:vid WHERE id=:oid",
                                            {"did": a["driver_id"], "vid": a["vehicle_id"], "oid": a["order_id"]}
                                        )
                                        count += 1
                                st.success(f"🤖✅ {count} commandes assignées intelligemment par l'I.A.")
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Erreur API OpenAI (Code {response.status_code}) : {response.text}")
            except Exception as e:
                st.error(f"Erreur : {e}")

    st.markdown("---")
    st.write(f"### 1️⃣ Planning du {date_planning.strftime('%d/%m/%Y')}")
    try:
        df_plan = load_data("""
            SELECT o.id, c.name as client, o.service_type, o.requested_slot,
                   COALESCE(o.material, o.waste_type) as details,
                   s.address, o.status,
                   o.driver_id,
                   COALESCE(o.delivery_order, 0) as delivery_order,
                   CONCAT(d.first_name, ' ', d.last_name) as chauffeur,
                   v.license_plate as vehicule
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN sites s ON o.site_id = s.id
            LEFT JOIN drivers d ON o.driver_id = d.id
            LEFT JOIN vehicles v ON o.vehicle_id = v.id
            WHERE o.requested_date = :d AND o.status IN ('pending', 'planned', 'dispatched')
            ORDER BY o.driver_id NULLS FIRST, COALESCE(o.delivery_order, 0), o.id
        """, {"d": date_planning})

        df_drivers_sel = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true")
        df_vehicles_sel = load_data("SELECT id, license_plate, name, type FROM vehicles WHERE is_available = true")

        drv_dict = {None: "--- Choisir un chauffeur ---"}
        for _, r in df_drivers_sel.iterrows():
            drv_dict[r["id"]] = f"{r['first_name']} {r['last_name']}"

        veh_dict_sel = {None: "--- Choisir un véhicule ---"}
        trailer_dict = {None: "Aucune remorque"}
        for _, r in df_vehicles_sel.iterrows():
            label = f"{r['license_plate']} ({r['type']}) {r['name'] or ''}"
            veh_dict_sel[r["id"]] = label
            trailer_dict[r["id"]] = label

        selected_order_ids = []
        if df_plan.empty:
            st.info("Aucune commande à planifier pour cette date.")
        else:
            unassigned = df_plan[df_plan["driver_id"].isna()]
            assigned = df_plan[df_plan["driver_id"].notna()]

            # ── Commandes non assignées ──
            if not unassigned.empty:
                st.write("#### 🔴 Non assignées")
                for _, row in unassigned.iterrows():
                    c_chk, c_info = st.columns([0.5, 9.5])
                    with c_chk:
                        checked = st.checkbox("", key=f"chk_{row['id']}", label_visibility="collapsed")
                    with c_info:
                        st.write(f"**{row['client']}** — {row['service_type']} — {row['details'] or ''} ({row['requested_slot'] or '?'})")
                    if checked:
                        selected_order_ids.append(row["id"])

            # ── Grouper par chauffeur ──
            if not assigned.empty:
                grouped_drivers = assigned.groupby("driver_id")
                for driver_id, group in grouped_drivers:
                    group = group.sort_values("delivery_order")
                    driver_name = group.iloc[0]["chauffeur"] or f"Chauffeur #{driver_id}"
                    with st.expander(f"👤 {driver_name} — {len(group)} mission(s)", expanded=True):
                        for pos, (_, row) in enumerate(group.iterrows()):
                            order_ids_list = group["id"].tolist()
                            c_num, c_chk, c_label, c_up, c_dn, c_reassign, c_unassign = st.columns([0.5, 0.5, 6, 0.5, 0.5, 1.5, 1.5])
                            with c_num:
                                st.markdown(f"**#{pos+1}**")
                            with c_chk:
                                checked = st.checkbox("", key=f"chk_{row['id']}", label_visibility="collapsed")
                            with c_label:
                                st.write(f"**{row['client']}** — {row['service_type']} — {row['details'] or ''} ({row['requested_slot'] or '?'})")
                            # Bouton monter
                            with c_up:
                                if pos > 0:
                                    if st.button("⬆️", key=f"up_{row['id']}", help="Monter dans la tournée"):
                                        prev_id = order_ids_list[pos - 1]
                                        run_query("UPDATE orders SET delivery_order=:o WHERE id=:id", {"o": pos - 1, "id": row["id"]})
                                        run_query("UPDATE orders SET delivery_order=:o WHERE id=:id", {"o": pos, "id": prev_id})
                                        st.cache_data.clear()
                                        st.rerun()
                            # Bouton descendre
                            with c_dn:
                                if pos < len(group) - 1:
                                    if st.button("⬇️", key=f"dn_{row['id']}", help="Descendre dans la tournée"):
                                        next_id = order_ids_list[pos + 1]
                                        run_query("UPDATE orders SET delivery_order=:o WHERE id=:id", {"o": pos + 1, "id": row["id"]})
                                        run_query("UPDATE orders SET delivery_order=:o WHERE id=:id", {"o": pos, "id": next_id})
                                        st.cache_data.clear()
                                        st.rerun()
                            # Réassigner à un autre chauffeur
                            with c_reassign:
                                other_drivers = {k: v for k, v in drv_dict.items() if k != driver_id and k is not None}
                                if other_drivers:
                                    reassign_target = st.selectbox(
                                        "↪️ Réassigner",
                                        options=[None] + list(other_drivers.keys()),
                                        format_func=lambda x: "↪️ Réassigner..." if x is None else other_drivers.get(x, ""),
                                        key=f"reassign_sel_{row['id']}",
                                        label_visibility="collapsed"
                                    )
                                    if reassign_target is not None:
                                        # Compter les missions du nouveau chauffeur ce jour-là
                                        df_new_drv = df_plan[df_plan["driver_id"] == reassign_target]
                                        new_order = len(df_new_drv)
                                        run_query(
                                            "UPDATE orders SET driver_id=:did, delivery_order=:o WHERE id=:id",
                                            {"did": reassign_target, "o": new_order, "id": row["id"]}
                                        )
                                        st.cache_data.clear()
                                        st.rerun()
                            # Remettre en attente
                            with c_unassign:
                                if st.button("🔄 Attente", key=f"unassign_{row['id']}", help="Désassigner et remettre en attente"):
                                    run_query(
                                        "UPDATE orders SET status='pending', driver_id=NULL, vehicle_id=NULL, trailer_id=NULL, delivery_order=0 WHERE id=:id",
                                        {"id": row["id"]}
                                    )
                                    st.cache_data.clear()
                                    st.rerun()
                            if checked:
                                selected_order_ids.append(row["id"])

        st.markdown("---")
        st.write("### 2️⃣ Assigner les ressources à la sélection")
        c_as1, c_as2, c_as3 = st.columns(3)
        with c_as1:
            assign_driver = st.selectbox("Chauffeur", options=list(drv_dict.keys()), format_func=lambda x: drv_dict[x])
        with c_as2:
            assign_vehicle = st.selectbox("Véhicule", options=list(veh_dict_sel.keys()), format_func=lambda x: veh_dict_sel[x])
        with c_as3:
            assign_trailer = st.selectbox("Remorque (optionnel)", options=list(trailer_dict.keys()), format_func=lambda x: trailer_dict[x])

        if st.button("💾 Assigner la sélection", type="primary"):
            if not selected_order_ids:
                st.warning("Aucune commande sélectionnée.")
            else:
                # Calculer le delivery_order de départ pour ce chauffeur
                df_existing = df_plan[df_plan["driver_id"] == assign_driver] if assign_driver else pd.DataFrame()
                start_order = len(df_existing)
                for i_ord, oid in enumerate(selected_order_ids):
                    run_query("""
                        UPDATE orders SET status='planned', driver_id=:did, vehicle_id=:vid, trailer_id=:tid, delivery_order=:o
                        WHERE id=:oid
                    """, {"did": assign_driver, "vid": assign_vehicle, "tid": assign_trailer, "o": start_order + i_ord, "oid": oid})
                st.success(f"✅ {len(selected_order_ids)} commande(s) assignée(s).")
                st.cache_data.clear()
                st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SUIVI DU PARC DE BENNES
# ─────────────────────────────────────────────────────────────────────────────
elif navigation == "📍 Suivi du Parc de Bennes":
    st.title("📍 Suivi du Parc de Bennes")
    try:
        df_inv = load_data("SELECT size, total_count FROM skip_inventory ORDER BY size")
        df_out = load_data("""
            SELECT o.container_type as size, COUNT(*) as count_out, c.name as client,
                   s.address, s.gmaps_link
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN sites s ON o.site_id = s.id
            WHERE o.status IN ('planned', 'dispatched')
              AND o.service_type LIKE 'Benne - Pose%'
            GROUP BY o.container_type, c.name, s.address, s.gmaps_link
        """)

        total_fleet = int(df_inv['total_count'].sum()) if not df_inv.empty else 0
        total_out = int(df_out['count_out'].sum()) if not df_out.empty else 0
        total_depot = total_fleet - total_out

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📦 TOTAL BENNES FLOTTE", total_fleet)
        col_m2.metric("🏗️ BENNES CHEZ LES CLIENTS", total_out)
        col_m3.metric("🏢 BENNES DISPO (DÉPÔT)", total_depot)

        st.markdown("---")
        st.write("### 📊 État du stock détaillé par volume")
        if not df_inv.empty:
            for _, row in df_inv.iterrows():
                size = row['size']
                total = int(row['total_count'])
                out_df = df_out[df_out['size'] == size] if not df_out.empty else pd.DataFrame()
                out_count = int(out_df['count_out'].sum()) if not out_df.empty else 0
                dispo = total - out_count
                st.progress(out_count / total if total > 0 else 0, text=f"**{size}** — {out_count}/{total} chez clients ({dispo} au dépôt)")

        st.markdown("---")
        st.write("### 👥 Visualisation par Client")
        if not df_out.empty:
            client_names = df_out['client'].unique().tolist()
            sel_client = st.selectbox("Filtrer par client", ["Tous"] + client_names)
            df_view = df_out if sel_client == "Tous" else df_out[df_out['client'] == sel_client]
            for _, row in df_view.iterrows():
                st.write(f"**{row['client']}** — {row['size']} × {int(row['count_out'])}")
                st.write(f"📍 {row['address']}")
                if row['gmaps_link']:
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={requests.utils.quote(row['address'])}"
                    st.markdown(f"[🗺️ Voir sur Google Maps]({maps_url})")
                    lat, lon = extract_coords(row['gmaps_link'])
                    if lat and lon:
                        m = folium.Map(location=[lat, lon], zoom_start=15)
                        folium.Marker([lat, lon], popup=f"{row['client']} — {row['size']}").add_to(m)
                        st_folium(m, width=700, height=300)
        else:
            st.info("Aucune benne actuellement chez des clients.")
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GESTION DES CHAUFFEURS
# ─────────────────────────────────────────────────────────────────────────────
elif navigation == "👥 Gestion des Chauffeurs":
    st.title("👥 Gestion des Chauffeurs")

    with st.expander("Ouvrir le formulaire d'ajout"):
        with st.form("add_driver_form"):
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                d_prenom = st.text_input("Prénom *")
                d_nom = st.text_input("Nom *")
                d_nationality = st.text_input("Nationalité", value="Français")
                d_tel = st.text_input("Téléphone")
                d_email = st.text_input("Email (utilisé pour la connexion)")
                d_whatsapp = st.text_input("WhatsApp (ex: +336...)")
                d_password = st.text_input("Mot de passe app chauffeur", type="password")
                d_password2 = st.text_input("Confirmer le mot de passe", type="password")
                d_notes = st.text_area("Période d'absence (ex: Congés du 12 au 20 Août)")
            with c_d2:
                d_permis = st.text_input("N° de Permis de Conduire")
                st.write("CACES / Habilitations")
                d_caces = st.checkbox("CACES Grue Auxiliaire")
                d_fimo_exp = st.date_input("Validité FIMO / FCO *", value=datetime.date.today() + datetime.timedelta(days=365), format="DD/MM/YYYY")
                d_carte_num = st.text_input("N° Carte Conducteur")
                d_carte_exp = st.date_input("Validité Carte Conducteur *", value=datetime.date.today() + datetime.timedelta(days=365), format="DD/MM/YYYY")
                d_caces_exp = st.date_input("Validité CACES (général)", value=datetime.date.today() + datetime.timedelta(days=365), format="DD/MM/YYYY")

            submitted_d = st.form_submit_button("➕ Ajouter le chauffeur", type="primary")
            if submitted_d:
                if not d_prenom or not d_nom:
                    st.error("Prénom et Nom sont obligatoires.")
                else:
                    try:
                        # Stocker WhatsApp dans notes avec préfixe WA:
                        notes_final = d_notes or ""
                        if d_whatsapp:
                            notes_final = f"WA:{d_whatsapp}\n{notes_final}".strip()
                        import hashlib as _hl
                        pw_errors = []
                        if d_password and d_password != d_password2:
                            pw_errors.append("Les mots de passe ne correspondent pas.")
                        if d_password and len(d_password) < 6:
                            pw_errors.append("Mot de passe trop court (6 caractères min).")
                        if pw_errors:
                            for pe in pw_errors:
                                st.error(pe)
                        else:
                            drv_pw_hash = _hl.sha256(d_password.encode()).hexdigest() if d_password else None
                            run_query("""
                                INSERT INTO drivers (first_name, last_name, phone, email, nationality,
                                    license_expiry, fimo_fco_expiry, driver_card_number, driver_card_expiry,
                                    caces_expiry, notes, is_active, password_hash)
                                VALUES (:fn, :ln, :ph, :em, :nat, :le, :fimo, :dcn, :dce, :ce, :notes, true, :pw)
                            """, {
                                "fn": d_prenom, "ln": d_nom, "ph": d_tel, "em": d_email,
                                "nat": d_nationality, "le": None, "fimo": d_fimo_exp,
                                "dcn": d_carte_num, "dce": d_carte_exp, "ce": d_caces_exp,
                                "notes": notes_final, "pw": drv_pw_hash
                            })
                        st.success(f"✅ Chauffeur {d_prenom} {d_nom} ajouté !")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    st.write("### 📋 Liste des Chauffeurs")
    try:
        df_drv_list = load_data("""
            SELECT id, first_name as "Prénom", last_name as "Nom",
                   nationality as "Nationalité", phone as "Téléphone",
                   email as "Email", notes as "Notes/Absences",
                   license_expiry as "Permis exp.", fimo_fco_expiry as "FCO exp.",
                   driver_card_expiry as "Carte Cond. exp."
            FROM drivers ORDER BY first_name
        """)
        if df_drv_list.empty:
            st.info("Aucun chauffeur enregistré.")
        else:
            st.dataframe(df_drv_list.drop(columns=['id']), use_container_width=True)
    except Exception as e:
        st.error(f"Erreur : {e}")

    st.write("### ✏️ Éditer / Supprimer un chauffeur")
    try:
        df_drv_sel = load_data("SELECT id, first_name, last_name FROM drivers ORDER BY first_name")
        if not df_drv_sel.empty:
            drv_edit_dict = dict(zip(df_drv_sel['id'], df_drv_sel['first_name'] + " " + df_drv_sel['last_name']))
            edit_drv_id = st.selectbox("Chauffeur à éditer", options=[None] + list(drv_edit_dict.keys()),
                                        format_func=lambda x: "--- Choisir ---" if x is None else drv_edit_dict[x])
            if edit_drv_id:
                df_edit = load_data("SELECT * FROM drivers WHERE id = :id", {"id": edit_drv_id})
                r = df_edit.iloc[0]
                # Extraire WhatsApp depuis les notes
                notes_raw = r['notes'] or ""
                wa_val = ""
                notes_display = notes_raw
                if notes_raw.startswith("WA:"):
                    lines = notes_raw.split("\n", 1)
                    wa_val = lines[0][3:].strip()
                    notes_display = lines[1].strip() if len(lines) > 1 else ""

                with st.form("edit_driver_form"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        e_prenom = st.text_input("Prénom", value=r['first_name'] or "")
                        e_nom = st.text_input("Nom", value=r['last_name'] or "")
                        e_nationality = st.text_input("Nationalité", value=r['nationality'] or "Français")
                        e_tel = st.text_input("Téléphone", value=r['phone'] or "")
                        e_email = st.text_input("Email", value=r['email'] or "")
                        e_whatsapp = st.text_input("WhatsApp", value=wa_val)
                        e_notes = st.text_area("Absences", value=notes_display)
                        st.markdown("**Nouveau mot de passe** (laisser vide pour ne pas changer)")
                        e_pw = st.text_input("Nouveau mot de passe", type="password", key="edit_drv_pw")
                        e_pw2 = st.text_input("Confirmer", type="password", key="edit_drv_pw2")
                    with ec2:
                        e_fimo = st.date_input("Validité FIMO/FCO", value=r['fimo_fco_expiry'] if pd.notna(r['fimo_fco_expiry']) else datetime.date.today(), format="DD/MM/YYYY")
                        e_dcnum = st.text_input("N° Carte Conducteur", value=r['driver_card_number'] or "")
                        e_dcexp = st.date_input("Validité Carte Conducteur", value=r['driver_card_expiry'] if pd.notna(r['driver_card_expiry']) else datetime.date.today(), format="DD/MM/YYYY")
                        e_caces = st.date_input("Validité CACES", value=r['caces_expiry'] if pd.notna(r['caces_expiry']) else datetime.date.today(), format="DD/MM/YYYY")
                        e_active = st.checkbox("Actif", value=bool(r['is_active']))
                    e_sub = st.form_submit_button("💾 Enregistrer les modifications", type="primary")
                    if e_sub:
                        # Recomposer les notes
                        new_notes = e_notes or ""
                        if e_whatsapp:
                            new_notes = f"WA:{e_whatsapp}\n{new_notes}".strip()
                        import hashlib as _hl2
                        if e_pw and e_pw != e_pw2:
                            st.error("Les mots de passe ne correspondent pas.")
                        elif e_pw and len(e_pw) < 6:
                            st.error("Mot de passe trop court (6 caractères min).")
                        else:
                            new_pw_hash = _hl2.sha256(e_pw.encode()).hexdigest() if e_pw else None
                            if new_pw_hash:
                                run_query("""
                                    UPDATE drivers SET first_name=:fn, last_name=:ln, phone=:ph, email=:em,
                                        nationality=:nat, fimo_fco_expiry=:fimo, driver_card_number=:dcn,
                                        driver_card_expiry=:dce, caces_expiry=:ce, notes=:notes, is_active=:active,
                                        password_hash=:pw
                                    WHERE id=:id
                                """, {
                                    "fn": e_prenom, "ln": e_nom, "ph": e_tel, "em": e_email,
                                    "nat": e_nationality, "fimo": e_fimo, "dcn": e_dcnum,
                                    "dce": e_dcexp, "ce": e_caces, "notes": new_notes,
                                    "active": e_active, "pw": new_pw_hash, "id": edit_drv_id
                                })
                            else:
                                run_query("""
                                    UPDATE drivers SET first_name=:fn, last_name=:ln, phone=:ph, email=:em,
                                        nationality=:nat, fimo_fco_expiry=:fimo, driver_card_number=:dcn,
                                        driver_card_expiry=:dce, caces_expiry=:ce, notes=:notes, is_active=:active
                                    WHERE id=:id
                                """, {
                                    "fn": e_prenom, "ln": e_nom, "ph": e_tel, "em": e_email,
                                    "nat": e_nationality, "fimo": e_fimo, "dcn": e_dcnum,
                                    "dce": e_dcexp, "ce": e_caces, "notes": new_notes,
                                    "active": e_active, "id": edit_drv_id
                                })
                            st.success("✅ Chauffeur mis à jour.")
                            st.cache_data.clear()
                            st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GESTION DE LA FLOTTE
# ─────────────────────────────────────────────────────────────────────────────
elif navigation == "🚚 Gestion de la Flotte":
    st.title("🚚 Gestion de la Flotte")

    with st.expander("➕ Ajouter un Véhicule"):
        with st.form("add_vehicle_form"):
            cv1, cv2 = st.columns(2)
            with cv1:
                v_plate = st.text_input("Immatriculation *")
                v_name = st.text_input("Nom personnalisé / Réf interne")
                v_brand = st.text_input("Marque")
                v_model = st.text_input("Modèle")
                v_type = st.selectbox("Type de véhicule", ["Camion benne", "Camion grue", "Porteur", "Semi-remorque", "Remorque", "Autre"])
                v_is_trailer = st.checkbox("Ce véhicule est remorqueur (attelage)")
            with cv2:
                v_ct = st.date_input("Date CT (Contrôle Technique)", value=datetime.date.today() + datetime.timedelta(days=365), format="DD/MM/YYYY")
                v_tacho = st.date_input("Chronotachygraphe valide jusqu'au", value=datetime.date.today() + datetime.timedelta(days=365), format="DD/MM/YYYY")
                v_limiter = st.date_input("Limiteur de vitesse valide jusqu'au", value=datetime.date.today() + datetime.timedelta(days=365), format="DD/MM/YYYY")
            v_sub = st.form_submit_button("➕ Ajouter le véhicule", type="primary")
            if v_sub:
                if not v_plate:
                    st.error("L'immatriculation est obligatoire.")
                else:
                    try:
                        run_query("""
                            INSERT INTO vehicles (name, brand, model, license_plate, type, is_trailer,
                                control_valid_until, tachograph_valid_until, speed_limiter_valid_until, is_available)
                            VALUES (:name, :brand, :model, :plate, :type, :trailer, :ct, :tacho, :limiter, true)
                        """, {
                            "name": v_name, "brand": v_brand, "model": v_model, "plate": v_plate,
                            "type": v_type, "trailer": v_is_trailer, "ct": v_ct,
                            "tacho": v_tacho, "limiter": v_limiter
                        })
                        st.success(f"✅ Véhicule {v_plate} ajouté !")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    st.write("### 📋 Liste de la Flotte")
    try:
        df_fleet = load_data("""
            SELECT id, license_plate, name, brand, model, type,
                   control_valid_until, tachograph_valid_until, speed_limiter_valid_until, is_available
            FROM vehicles ORDER BY license_plate
        """)
        if df_fleet.empty:
            st.info("Aucun véhicule enregistré.")
        else:
            st.dataframe(df_fleet.drop(columns=['id']), use_container_width=True)
    except Exception as e:
        st.error(f"Erreur : {e}")

    st.write("### ✏️ Éditer un véhicule")
    try:
        df_veh_sel = load_data("SELECT id, license_plate, name FROM vehicles ORDER BY license_plate")
        if not df_veh_sel.empty:
            veh_edit_dict = dict(zip(df_veh_sel['id'], df_veh_sel['license_plate'] + " " + df_veh_sel['name'].fillna('')))
            edit_veh_id = st.selectbox("Véhicule à éditer", options=[None] + list(veh_edit_dict.keys()),
                                        format_func=lambda x: "--- Choisir ---" if x is None else veh_edit_dict[x])
            if edit_veh_id:
                df_ev = load_data("SELECT * FROM vehicles WHERE id = :id", {"id": edit_veh_id})
                rv = df_ev.iloc[0]
                with st.form("edit_vehicle_form"):
                    ev1, ev2 = st.columns(2)
                    with ev1:
                        ev_plate = st.text_input("Immatriculation", value=rv['license_plate'] or "")
                        ev_name = st.text_input("Nom / Réf", value=rv['name'] or "")
                        ev_brand = st.text_input("Marque", value=rv['brand'] or "")
                        ev_model = st.text_input("Modèle", value=rv['model'] or "")
                        ev_type = st.text_input("Type", value=rv['type'] or "")
                        ev_avail = st.checkbox("Disponible", value=bool(rv['is_available']))
                    with ev2:
                        ev_ct = st.date_input("CT valide jusqu'au", value=rv['control_valid_until'] if pd.notna(rv['control_valid_until']) else datetime.date.today(), format="DD/MM/YYYY")
                        ev_tacho = st.date_input("Chronotachygraphe valide jusqu'au", value=rv['tachograph_valid_until'] if pd.notna(rv['tachograph_valid_until']) else datetime.date.today(), format="DD/MM/YYYY")
                        ev_limiter = st.date_input("Limiteur valide jusqu'au", value=rv['speed_limiter_valid_until'] if pd.notna(rv['speed_limiter_valid_until']) else datetime.date.today(), format="DD/MM/YYYY")
                    ev_sub = st.form_submit_button("💾 Enregistrer", type="primary")
                    if ev_sub:
                        run_query("""
                            UPDATE vehicles SET license_plate=:plate, name=:name, brand=:brand, model=:model,
                                type=:type, control_valid_until=:ct, tachograph_valid_until=:tacho,
                                speed_limiter_valid_until=:limiter, is_available=:avail
                            WHERE id=:id
                        """, {
                            "plate": ev_plate, "name": ev_name, "brand": ev_brand, "model": ev_model,
                            "type": ev_type, "ct": ev_ct, "tacho": ev_tacho, "limiter": ev_limiter,
                            "avail": ev_avail, "id": edit_veh_id
                        })
                        st.success("✅ Véhicule mis à jour.")
                        st.cache_data.clear()
                        st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")

    st.write("### 🚨 Signaler un problème véhicule (Admin)")
    with st.expander("Ouvrir le formulaire de signalement"):
        with st.form("admin_issue_form"):
            try:
                df_veh_issue = load_data("SELECT id, license_plate, name FROM vehicles WHERE is_available = true")
                veh_issue_dict = dict(zip(df_veh_issue['id'], df_veh_issue['license_plate'] + " " + df_veh_issue['name'].fillna('')))
            except Exception:
                veh_issue_dict = {}
            admin_veh_id = st.selectbox("Véhicule concerné", options=[None] + list(veh_issue_dict.keys()),
                                         format_func=lambda x: "--- Choisir ---" if x is None else veh_issue_dict.get(x, ""))
            admin_desc = st.text_area("Description du problème")
            admin_photo_file = st.file_uploader("Photo (optionnelle)", type=["jpg", "jpeg", "png"])
            admin_submitted = st.form_submit_button("🚨 Signaler", type="primary")
            if admin_submitted:
                if admin_veh_id and admin_desc:
                    admin_photo_path = ""
                    if admin_photo_file is not None:
                        os.makedirs("uploads/photos", exist_ok=True)
                        filename = f"{uuid.uuid4().hex}.jpg"
                        filepath = os.path.join("uploads/photos", filename)
                        with open(filepath, "wb") as f:
                            f.write(admin_photo_file.getbuffer())
                        admin_photo_path = filepath
                    run_query(
                        "INSERT INTO vehicle_issues (vehicle_id, description, photo_data) VALUES (:vid, :desc, :pic)",
                        {"vid": admin_veh_id, "desc": "[Signalement Admin] " + admin_desc, "pic": admin_photo_path}
                    )
                    st.success("✅ Problème signalé !")
                    st.cache_data.clear()
                else:
                    st.error("Véhicule et description obligatoires.")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: VUE CHAUFFEUR (MOBILE)
# ─────────────────────────────────────────────────────────────────────────────
elif navigation == "📱 Vue Chauffeur (Mobile)":
    st.title("📱 Vue Chauffeur (Mobile)")

    try:
        df_drv_mobile = load_data("SELECT id, first_name, last_name, nationality FROM drivers WHERE is_active = true ORDER BY first_name")
        if df_drv_mobile.empty:
            st.warning("Aucun chauffeur actif.")
            st.stop()

        drv_mobile_dict = dict(zip(df_drv_mobile['id'], df_drv_mobile['first_name'] + " " + df_drv_mobile['last_name']))
        # Si connecté en tant que chauffeur, pré-sélectionner et verrouiller
        if st.session_state.auth_role == "driver":
            chauffeur_id = st.session_state.auth_driver_id
            st.info(f"🚚 Connecté : **{drv_mobile_dict.get(chauffeur_id, chauffeur_id)}**")
        else:
            chauffeur_id = st.selectbox("Se connecter en tant que :", options=list(drv_mobile_dict.keys()),
                                         format_func=lambda x: drv_mobile_dict[x])

        # Détecter langue selon nationalité
        drv_row = df_drv_mobile[df_drv_mobile['id'] == chauffeur_id].iloc[0]
        L = get_lang(drv_row.get('nationality', 'Français'))

        today_mobile = datetime.date.today()

        # 5a. Véhicule assigné UNIQUEMENT depuis orders du jour
        df_assigned = load_data("""
            SELECT o.vehicle_id as truck_id, v.license_plate as truck_label,
                   o.trailer_id as t_id, tr.license_plate as trailer_label
            FROM orders o
            LEFT JOIN vehicles v ON o.vehicle_id = v.id
            LEFT JOIN vehicles tr ON o.trailer_id = tr.id
            WHERE o.driver_id = :did AND o.requested_date = :d
            LIMIT 1
        """, {"did": chauffeur_id, "d": today_mobile})

        assigned_truck_id = None
        assigned_truck_label = "Aucun"
        assigned_trailer_id = None
        assigned_trailer_label = None

        if not df_assigned.empty:
            row_a = df_assigned.iloc[0]
            assigned_truck_id = row_a['truck_id']
            assigned_truck_label = row_a['truck_label'] or "Aucun"
            if pd.notna(row_a.get('t_id')):
                assigned_trailer_id = row_a['t_id']
                assigned_trailer_label = row_a['trailer_label']

        st.write(f"### {L['my_vehicles']}")

        def issue_form_mobile(veh_id, form_key, veh_label):
            with st.expander(f"🚨 Signaler problème : {veh_label}"):
                with st.form(form_key):
                    issue_type = st.selectbox(L['issue_type'], ["Pneu usé / crevé", "Feu cassé", "Carrosserie endommagée", "Intérieur sale", "Problème moteur / Voyant", "Autre"])
                    desc = st.text_area(L['issue_desc'], placeholder="Ex: Feu arrière droit brisé en reculant ce matin...")
                    photo_cam = st.camera_input("📸 Prendre une photo")
                    photo_file = st.file_uploader("📎 Ou importer une photo", type=["jpg", "jpeg", "png"], key=f"upl_{form_key}")
                    submitted = st.form_submit_button("🚀 Envoyer le signalement", type="primary", use_container_width=True)
                    if submitted:
                        if veh_id and desc:
                            photo_path = ""
                            photo_src = photo_cam or photo_file
                            if photo_src is not None:
                                os.makedirs("uploads/photos", exist_ok=True)
                                filename = f"{uuid.uuid4().hex}.jpg"
                                filepath = os.path.join("uploads/photos", filename)
                                with open(filepath, "wb") as f:
                                    f.write(photo_src.getbuffer())
                                photo_path = filepath
                            run_query(
                                "INSERT INTO vehicle_issues (driver_id, vehicle_id, description, photo_data) VALUES (:did, :vid, :desc, :pic)",
                                {"did": chauffeur_id, "vid": veh_id, "desc": f"[{issue_type}] {desc}", "pic": photo_path}
                            )
                            st.success("✅ Problème signalé !")
                        else:
                            st.error("⚠️ Description obligatoire.")

        if assigned_truck_id:
            issue_form_mobile(assigned_truck_id, "form_truck", f"{L['assigned_truck']} : {assigned_truck_label}")
            if assigned_trailer_label:
                issue_form_mobile(assigned_trailer_id, "form_trailer", f"{L['assigned_trailer']} : {assigned_trailer_label}")
        else:
            st.warning(L['no_vehicle'])

        st.divider()
        st.write(f"### 📋 {L['my_missions']}")

        # 5b. Missions avec détails selon type
        df_missions = load_data("""
            SELECT o.id, c.name as client_name, c.phone as client_phone,
                   s.address, s.gmaps_link,
                   o.service_type, o.material, o.waste_type,
                   o.quantity_tons, o.requested_slot, o.instructions,
                   o.status, o.container_type, o.loading_point, o.unloading_point
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN sites s ON o.site_id = s.id
            WHERE o.driver_id = :did AND o.requested_date = :d
            ORDER BY COALESCE(o.delivery_order, 0), o.id
        """, {"did": chauffeur_id, "d": today_mobile})

        if df_missions.empty:
            st.info(L['no_mission'])
        else:
            for _, m in df_missions.iterrows():
                stype = str(m['service_type'] or "").lower()
                is_benne_mission = any(x in stype for x in [
                    "benne", "pose", "retrait", "rotation", "enlèvement", "enlevement", "déplacement"
                ])
                is_rotation_enlev = any(x in stype for x in ["rotation", "enlèvement", "enlevement", "déplacement", "retrait"])

                mission_label = f"📦 {m['client_name']} — {m['service_type']} ({m['requested_slot'] or '?'})"
                with st.expander(mission_label):
                    # Détails selon type de prestation
                    st.write(f"**{L['client']} :** {m['client_name']}")
                    st.write(f"**{L['address']} :** {m['address']}")

                    if m['gmaps_link']:
                        st.markdown(f"[{L['open_maps']}]({m['gmaps_link']})")

                    if m['client_phone']:
                        st.write(f"**{L['phone']} :** {m['client_phone']}")

                    if not is_benne_mission:
                        # Livraison matériaux
                        if m['material']:
                            st.write(f"**{L['product']} :** {m['material']}")
                        if m['quantity_tons']:
                            st.write(f"**{L['quantity']} :** {m['quantity_tons']} t")
                        if m['loading_point']:
                            st.write(f"**{L['loading_point']} :** {m['loading_point']}")
                    else:
                        # Location benne
                        if m['waste_type']:
                            st.write(f"**{L['waste']} :** {m['waste_type']}")
                        if m['container_type']:
                            st.write(f"**{L['container_size']} :** {m['container_type']}")
                        if is_rotation_enlev and m['unloading_point']:
                            st.write(f"**{L['unloading_point']} :** {m['unloading_point']}")

                    st.write(f"**{L['slot']} :** {m['requested_slot'] or '?'}")

                    if m['instructions']:
                        st.info(f"💬 {L['comment']} : {m['instructions']}")

                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        if st.button(L['delivered'], key=f"done_{m['id']}", use_container_width=True, type="primary"):
                            run_query("UPDATE orders SET status='done' WHERE id=:id", {"id": m['id']})
                            st.success("Mission validée !")
                            st.cache_data.clear()
                            st.rerun()
                    with col_m2:
                        # 5c. Signalement problème (bouton toggle - sans expander imbriqué)
                        toggle_key = f"show_issue_{m['id']}"
                        if st.button(L['report_issue'], key=f"btn_issue_{m['id']}", use_container_width=True):
                            st.session_state[toggle_key] = not st.session_state.get(toggle_key, False)
                        if st.session_state.get(toggle_key, False):
                            with st.form(f"mission_issue_{m['id']}"):
                                issue_desc = st.text_area(L['issue_desc'])
                                issue_photo_cam = st.camera_input("📸 Prendre une photo")
                                issue_photo_file = st.file_uploader("📎 Ou importer", type=["jpg", "jpeg", "png"], key=f"ph_{m['id']}")
                                if st.form_submit_button(L['send_alert'], type="primary", use_container_width=True):
                                    if issue_desc:
                                        pic_path = ""
                                        photo_src = issue_photo_cam or issue_photo_file
                                        if photo_src is not None:
                                            os.makedirs("uploads/photos", exist_ok=True)
                                            filename = f"{uuid.uuid4().hex}.jpg"
                                            filepath = os.path.join("uploads/photos", filename)
                                            with open(filepath, "wb") as f:
                                                f.write(photo_src.getbuffer())
                                            pic_path = filepath
                                        run_query(
                                            "INSERT INTO order_issues (order_id, driver_id, description, photo_data) VALUES (:oid, :did, :desc, :pic)",
                                            {"oid": m['id'], "did": chauffeur_id, "desc": issue_desc, "pic": pic_path}
                                        )
                                        st.session_state[toggle_key] = False
                                        st.success("🚨 Alerte envoyée au bureau !")
                                    else:
                                        st.error("La description est obligatoire.")
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CENTRE DE TRI
# ─────────────────────────────────────────────────────────────────────────────
elif navigation == "♻️ Centre de Tri":
    st.title("♻️ Centre de Tri")
    st.caption("Gestion des bennes internes du centre de tri")

    try:
        df_bins = load_data("SELECT id, bin_type, container_size, status, notes FROM sorting_center_bins ORDER BY bin_type")

        if df_bins.empty:
            st.info("Aucune benne enregistrée dans le centre de tri.")
        else:
            st.write("### 🗑️ État des bennes")
            for _, bin_row in df_bins.iterrows():
                col_info, col_action = st.columns([3, 1])
                is_full = str(bin_row['status']).lower() == 'full'
                fill_ratio = 1.0 if is_full else 0.5
                status_label = "🔴 PLEINE" if is_full else "🟢 OK"

                with col_info:
                    st.write(f"**{bin_row['bin_type']}** ({bin_row['container_size']}) — {status_label}")
                    if bin_row['notes']:
                        st.caption(f"Note : {bin_row['notes']}")

                with col_action:
                    if not is_full:
                        if st.button(f"🚨 Marquer PLEINE", key=f"full_{bin_row['id']}"):
                            run_query("UPDATE sorting_center_bins SET status='full' WHERE id=:id", {"id": bin_row['id']})
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        if st.button(f"📋 Créer enlèvement", key=f"create_order_{bin_row['id']}", type="primary"):
                            try:
                                run_query("""
                                    INSERT INTO orders (service_type, waste_type, status, source, requested_date, instructions)
                                    VALUES ('Location de benne', :waste, 'pending', 'centre_tri', CURRENT_DATE, :notes)
                                """, {
                                    "waste": bin_row['bin_type'],
                                    "notes": f"Enlèvement benne centre de tri - {bin_row['bin_type']} ({bin_row['container_size']})"
                                })
                                run_query("UPDATE sorting_center_bins SET status='ok' WHERE id=:id", {"id": bin_row['id']})
                                st.success(f"✅ Commande d'enlèvement créée pour {bin_row['bin_type']} !")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur création commande : {e}")
                st.divider()

        # Ajouter une benne
        with st.expander("➕ Ajouter une benne au centre"):
            with st.form("add_bin_form"):
                new_bin_type = st.text_input("Type de benne (ex: Bois, Placo, Carton...)")
                new_bin_size = st.text_input("Taille", value="10m3")
                new_bin_notes = st.text_area("Notes")
                if st.form_submit_button("➕ Ajouter"):
                    if new_bin_type:
                        try:
                            run_query("""
                                INSERT INTO sorting_center_bins (bin_type, container_size, status, notes)
                                VALUES (:bt, :bs, 'ok', :notes)
                                ON CONFLICT (bin_type) DO NOTHING
                            """, {"bt": new_bin_type, "bs": new_bin_size, "notes": new_bin_notes})
                            st.success(f"Benne {new_bin_type} ajoutée !")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                    else:
                        st.error("Le type est obligatoire.")
    except Exception as e:
        st.error(f"Erreur centre de tri : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PARAMÈTRES DE L'ENTREPRISE
# ─────────────────────────────────────────────────────────────────────────────
elif navigation == "⚙️ Paramètres de l'Entreprise":
    st.title("⚙️ Paramètres de l'Entreprise")

    # Inventaire global
    st.write("### 📊 Inventaire Global")
    try:
        df_inv_param = load_data("SELECT size, total_count FROM skip_inventory ORDER BY size")
        if not df_inv_param.empty:
            cols_inv = st.columns(len(df_inv_param))
            for i, (_, row) in enumerate(df_inv_param.iterrows()):
                cols_inv[i].metric(f"Quantité Totale Possédée", row['total_count'], label_visibility="visible")
                cols_inv[i].caption(row['size'])
    except Exception as e:
        st.error(f"Erreur inventaire : {e}")

    st.markdown("---")
    st.write("### 🔒 Modification Sécurisée")
    # 6a. PIN = "2026"
    pin_input = st.text_input("Code PIN Admin", type="password", max_chars=10)
    pin_ok = False
    if pin_input:
        try:
            df_pin = load_data("SELECT value FROM system_settings WHERE key='admin_pin'")
            stored_pin = df_pin.iloc[0]['value'] if not df_pin.empty else "2026"
            if pin_input == stored_pin:
                pin_ok = True
                st.success("Accès Admin Déverrouillé 🔓")
            else:
                st.error("PIN incorrect.")
        except Exception:
            if pin_input == "2026":
                pin_ok = True
                st.success("Accès Admin Déverrouillé 🔓")

    if pin_ok:
        try:
            df_inv_edit = load_data("SELECT size, total_count FROM skip_inventory ORDER BY size")
            new_counts = {}
            st.write("Modifier les quantités :")
            cols_edit = st.columns(len(df_inv_edit))
            for i, (_, row) in enumerate(df_inv_edit.iterrows()):
                with cols_edit[i]:
                    new_counts[row['size']] = st.number_input(f"{row['size']}", min_value=0, value=int(row['total_count']), key=f"inv_{row['size']}")
            if st.button("💾 Enregistrer le nouveau stock", type="primary"):
                for size, count in new_counts.items():
                    run_query("UPDATE skip_inventory SET total_count=:cnt WHERE size=:s", {"cnt": count, "s": size})
                st.success("✅ Stock mis à jour !")
                st.cache_data.clear()
                st.rerun()
        except Exception as e:
            st.error(f"Erreur : {e}")

        st.markdown("---")
        st.write("### ➕ Ajouter un nouveau volume de benne")
        with st.form("add_skip_size"):
            new_size = st.text_input("Volume (ex: 20m3)")
            new_count = st.number_input("Quantité initiale", min_value=0, value=1)
            if st.form_submit_button("➕ Ajouter"):
                if new_size:
                    try:
                        run_query("INSERT INTO skip_inventory (size, total_count) VALUES (:s, :c) ON CONFLICT DO NOTHING", {"s": new_size, "c": new_count})
                        st.success(f"Volume {new_size} ajouté !")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

        st.markdown("---")
        st.write("### 🗑️ Supprimer un volume de benne")
        try:
            df_inv_del = load_data("SELECT size FROM skip_inventory ORDER BY size")
            if not df_inv_del.empty:
                del_size = st.selectbox("Volume à supprimer", df_inv_del['size'].tolist())
                st.warning(f"⚠️ Attention : la suppression du volume {del_size} est irréversible !")
                if st.button("🗑️ Supprimer ce volume", type="secondary"):
                    run_query("DELETE FROM skip_inventory WHERE size=:s", {"s": del_size})
                    st.success(f"Volume {del_size} supprimé.")
                    st.cache_data.clear()
                    st.rerun()
        except Exception as e:
            st.error(f"Erreur : {e}")

    st.markdown("---")
    # 6b-6d. Catalogue avec onglets corrigés
    st.write("### 🛒 Catalogue")

    tab_mat, tab_waste, tab_stype, tab_load, tab_unload = st.tabs([
        "📦 Matériaux",
        "🗑️ Déchets (Bennes)",
        "🏷️ Types de prestation",
        "📍 Points de chargement",
        "📍 Points de déchargement",
    ])

    def render_catalog_tab(category, tab_label):
        """Rendu générique d'un onglet catalogue."""
        try:
            df_cat = load_data(
                "SELECT id, name FROM catalog_items WHERE category=:cat ORDER BY name",
                {"cat": category}
            )
            if df_cat.empty:
                st.info(f"Aucun élément dans {tab_label}.")
            else:
                for _, cat_row in df_cat.iterrows():
                    col_n, col_d = st.columns([4, 1])
                    col_n.write(f"• {cat_row['name']}")
                    if pin_ok:
                        if col_d.button("🗑️", key=f"del_cat_{category}_{cat_row['id']}"):
                            run_query("DELETE FROM catalog_items WHERE id=:id", {"id": cat_row['id']})
                            st.cache_data.clear()
                            st.rerun()
            if pin_ok:
                with st.form(f"add_{category}"):
                    new_name = st.text_input(f"Nouveau ({tab_label})", key=f"inp_{category}")
                    if st.form_submit_button("➕ Ajouter"):
                        if new_name:
                            try:
                                run_query(
                                    "INSERT INTO catalog_items (category, name) VALUES (:cat, :name) ON CONFLICT DO NOTHING",
                                    {"cat": category, "name": new_name}
                                )
                                st.success(f"'{new_name}' ajouté !")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur : {e}")
        except Exception as e:
            st.error(f"Erreur catalogue {tab_label} : {e}")

    with tab_mat:
        render_catalog_tab("material", "Matériaux")
    with tab_waste:
        render_catalog_tab("waste", "Déchets")
    with tab_stype:
        # 6c. Types de prestation avec valeurs initiales
        try:
            run_query("""
                INSERT INTO catalog_items (category, name)
                VALUES ('service_type', 'Livraison de matériaux'),
                       ('service_type', 'Location de benne')
                ON CONFLICT DO NOTHING
            """)
        except Exception:
            pass
        render_catalog_tab("service_type", "Types de prestation")
    with tab_load:
        # 6d. Points de chargement
        render_catalog_tab("loading_point", "Points de chargement")
    with tab_unload:
        # 6d. Points de déchargement
        render_catalog_tab("unloading_point", "Points de déchargement")

    st.markdown("---")
    st.write("### 🔐 Identifiants Admin")
    if pin_ok:
        with st.form("admin_credentials_form"):
            df_creds = load_data("SELECT key, value FROM system_settings WHERE key IN ('admin_email','admin_password_hash')")
            creds = dict(zip(df_creds["key"], df_creds["value"])) if not df_creds.empty else {}
            ca1, ca2 = st.columns(2)
            with ca1:
                new_admin_email = st.text_input("Email admin", value=creds.get("admin_email", ""))
            with ca2:
                new_admin_pw = st.text_input("Nouveau mot de passe admin", type="password")
                new_admin_pw2 = st.text_input("Confirmer", type="password")
            if st.form_submit_button("💾 Mettre à jour les identifiants admin", type="primary"):
                import hashlib as _hla
                errors_cred = []
                if new_admin_pw and new_admin_pw != new_admin_pw2:
                    errors_cred.append("Les mots de passe ne correspondent pas.")
                if new_admin_pw and len(new_admin_pw) < 6:
                    errors_cred.append("Mot de passe trop court.")
                if errors_cred:
                    for ec in errors_cred:
                        st.error(ec)
                else:
                    if new_admin_email:
                        run_query("INSERT INTO system_settings (key,value) VALUES ('admin_email',:v) ON CONFLICT (key) DO UPDATE SET value=:v", {"v": new_admin_email})
                    if new_admin_pw:
                        run_query("INSERT INTO system_settings (key,value) VALUES ('admin_password_hash',:v) ON CONFLICT (key) DO UPDATE SET value=:v", {"v": _hla.sha256(new_admin_pw.encode()).hexdigest()})
                    st.success("✅ Identifiants admin mis à jour.")
                    st.cache_data.clear()

    st.markdown("---")
    st.write("### 📅 Jours de fermeture de l'entreprise")
    try:
        df_closures_view = load_data("SELECT start_date, end_date, reason FROM company_closures ORDER BY start_date")
        if not df_closures_view.empty:
            st.dataframe(df_closures_view, use_container_width=True)
        if pin_ok:
            with st.form("add_closure"):
                cc1, cc2 = st.columns(2)
                with cc1:
                    cl_start = st.date_input("Début de la fermeture", format="DD/MM/YYYY")
                    cl_end = st.date_input("Fin de la fermeture", format="DD/MM/YYYY")
                with cc2:
                    cl_reason = st.text_input("Motif (ex: Congés annuels)")
                if st.form_submit_button("📅 Ajouter la fermeture"):
                    run_query("INSERT INTO company_closures (start_date, end_date, reason) VALUES (:s, :e, :r)", {"s": cl_start, "e": cl_end, "r": cl_reason})
                    st.success("Fermeture ajoutée !")
                    st.cache_data.clear()
                    st.rerun()
    except Exception as e:
        st.error(f"Erreur fermetures : {e}")
