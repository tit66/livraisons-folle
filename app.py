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

DB_URI = 'postgresql://n8n:supersecret@n8n-local_postgres_1:5432/n8n'

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
                name VARCHAR(255),
                category VARCHAR(50),
                unit VARCHAR(50),
                price_ht NUMERIC(10,2)
            )
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
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
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

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🐙 Livraisons Folles")
    st.markdown("---")
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
            "⚙️ Paramètres de l'Entreprise",
        ]
    )

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: TABLEAU DE BORD
# ─────────────────────────────────────────────────────────────────────────────
if navigation == "📊 Tableau de bord - Livraisons":
    st.title("📊 Tableau de bord - Livraisons")
    today = datetime.date.today()
    date_filtre = st.date_input("Afficher les livraisons du :", value=today)

    try:
        df_orders = load_data("""
            SELECT o.id, c.name as "Client", o.status as "Statut",
                   o.service_type as "Prestation",
                   COALESCE(o.material, o.waste_type) as "Détails",
                   o.requested_slot as "Créneau",
                   CONCAT(d.first_name, ' ', d.last_name) as "Chauffeur",
                   v.license_plate as "Véhicule",
                   s.address as "Adresse"
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN drivers d ON o.driver_id = d.id
            LEFT JOIN vehicles v ON o.vehicle_id = v.id
            LEFT JOIN sites s ON o.site_id = s.id
            WHERE o.requested_date = :d
            ORDER BY o.id
        """, {"d": date_filtre})
        if df_orders.empty:
            st.info("Aucune livraison pour cette date.")
        else:
            st.dataframe(df_orders.drop(columns=['id']), use_container_width=True)
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
                with st.expander(f"🚨 {row['license_plate']} — {row['description'][:60]}..."):
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
                with st.expander(f"🚨 {row['client']} — {row['description'][:60]}"):
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
        prestation = st.radio("3️⃣ Type de Prestation", ["Livraison de matériaux", "Location de benne", "Autre"], horizontal=True)

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
        prestation = st.radio("3️⃣ Type de Prestation", ["Livraison de matériaux", "Location de benne", "Autre"], horizontal=True)
    else:
        prestation = None

    # Variables commandes
    marchandise = volume_benne = type_benne = action_benne = quantite = None
    instructions = ""
    date_livraison = datetime.date.today()
    creneau_choisi = "Matin"

    if prestation is not None:
        st.divider()
        if prestation == "Livraison de matériaux":
            df_mat = load_data("SELECT name FROM catalog_items WHERE category='material' ORDER BY name")
            mat_options = df_mat['name'].tolist() if not df_mat.empty else []
            mat_options_display = mat_options + ["Big Bag"]
            marchandise = st.selectbox("Matériau", mat_options_display)
            if marchandise == "Big Bag":
                st.warning("⚠️ **Avertissement de tarification :** La livraison en Big Bag se fait en camion grue. Tarification spécifique applicable.")
            quantite = st.number_input("Quantité (tonnes)", min_value=0.0, step=0.5, value=1.0)

        elif prestation == "Location de benne":
            action_benne = st.radio("Action", ["Pose", "Rotation", "Enlèvement", "Déplacement"], horizontal=True)
            df_waste = load_data("SELECT name FROM catalog_items WHERE category='waste' ORDER BY name")
            waste_options = df_waste['name'].tolist() if not df_waste.empty else []
            type_benne = st.selectbox("Type de déchets", waste_options) if waste_options else st.text_input("Type de déchets")
            df_inv = load_data("SELECT size FROM skip_inventory ORDER BY size")
            inv_options = df_inv['size'].tolist() if not df_inv.empty else []
            volume_benne = st.selectbox("Volume de benne", inv_options) if inv_options else st.text_input("Volume de benne")
            if type_benne and "gravat" in str(type_benne).lower():
                st.warning("⚠️ Pour les gravats, le volume maximum conseillé est de 10m3")

        st.divider()
        date_livraison = st.date_input("📅 Date souhaitée", value=datetime.date.today() + datetime.timedelta(days=1))
        est_valide, msg_valide = est_jour_ouvrable(date_livraison)
        if not est_valide:
            st.error(msg_valide)
        else:
            st.success(msg_valide)

        creneau_choisi = st.radio("Créneau", ["Matin", "Après-midi", "Journée entière"], horizontal=True)
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

                service_final = f"Benne - {action_benne}" if prestation == "Location de benne" else prestation
                run_query("""
                    INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons,
                        container_type, waste_type, instructions, status, source, requested_date, requested_slot)
                    VALUES (:client_id, :site_id, :service_type, :material, :quantity,
                        :container_type, :waste_type, :instructions, 'pending', 'admin_streamlit', :req_date, :req_slot)
                """, {
                    "client_id": final_client_id, "site_id": final_site_id, "service_type": service_final,
                    "material": marchandise, "quantity": quantite, "container_type": volume_benne,
                    "waste_type": type_benne, "instructions": instructions,
                    "req_date": date_livraison, "req_slot": creneau_choisi
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

    date_planning = st.date_input("Date du planning à préparer", value=datetime.date.today())

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
    st.write(f"### 1️⃣ Sélectionner les commandes du {date_planning.strftime('%d/%m/%Y')}")
    try:
        df_plan = load_data("""
            SELECT o.id, c.name as client, o.service_type, o.requested_slot,
                   COALESCE(o.material, o.waste_type) as details,
                   s.address, o.status,
                   CONCAT(d.first_name, ' ', d.last_name) as chauffeur,
                   v.license_plate as vehicule
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN sites s ON o.site_id = s.id
            LEFT JOIN drivers d ON o.driver_id = d.id
            LEFT JOIN vehicles v ON o.vehicle_id = v.id
            WHERE o.requested_date = :d AND o.status IN ('pending', 'planned')
            ORDER BY o.id
        """, {"d": date_planning})

        selected_order_ids = []
        if df_plan.empty:
            st.info("Aucune commande à planifier pour cette date.")
        else:
            for _, row in df_plan.iterrows():
                checked = st.checkbox(
                    f"[{row['status'].upper()}] {row['client']} — {row['service_type']} — {row['details']} ({row['requested_slot']})",
                    key=f"chk_{row['id']}"
                )
                if checked:
                    selected_order_ids.append(row['id'])

        st.write("### 2️⃣ Assigner les ressources à la sélection")
        df_drivers_sel = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true")
        df_vehicles_sel = load_data("SELECT id, license_plate, name, type FROM vehicles WHERE is_available = true")

        drv_dict = {None: "--- Choisir un chauffeur ---"}
        for _, r in df_drivers_sel.iterrows():
            drv_dict[r['id']] = f"{r['first_name']} {r['last_name']}"

        veh_dict_sel = {None: "--- Choisir un véhicule ---"}
        trailer_dict = {None: "Aucune remorque"}
        for _, r in df_vehicles_sel.iterrows():
            label = f"{r['license_plate']} ({r['type']}) {r['name'] or ''}"
            veh_dict_sel[r['id']] = label
            trailer_dict[r['id']] = label

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
                for oid in selected_order_ids:
                    run_query("""
                        UPDATE orders SET status='planned', driver_id=:did, vehicle_id=:vid, trailer_id=:tid
                        WHERE id=:oid
                    """, {"did": assign_driver, "vid": assign_vehicle, "tid": assign_trailer, "oid": oid})
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
            WHERE o.status IN ('planned', 'in_progress')
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
                d_tel = st.text_input("Téléphone")
                d_email = st.text_input("Email")
                d_notes = st.text_area("Période d'absence (ex: Congés du 12 au 20 Août)")
            with c_d2:
                d_permis = st.text_input("N° de Permis de Conduire")
                st.write("CACES / Habilitations")
                d_caces = st.checkbox("CACES Grue Auxiliaire")
                d_fimo_exp = st.date_input("Validité FIMO / FCO *", value=datetime.date.today() + datetime.timedelta(days=365))
                d_carte_num = st.text_input("N° Carte Conducteur")
                d_carte_exp = st.date_input("Validité Carte Conducteur *", value=datetime.date.today() + datetime.timedelta(days=365))
                d_caces_exp = st.date_input("Validité CACES (général)", value=datetime.date.today() + datetime.timedelta(days=365))

            submitted_d = st.form_submit_button("➕ Ajouter le chauffeur", type="primary")
            if submitted_d:
                if not d_prenom or not d_nom:
                    st.error("Prénom et Nom sont obligatoires.")
                else:
                    try:
                        run_query("""
                            INSERT INTO drivers (first_name, last_name, phone, email, license_expiry,
                                fimo_fco_expiry, driver_card_number, driver_card_expiry, caces_expiry,
                                notes, is_active)
                            VALUES (:fn, :ln, :ph, :em, :le, :fimo, :dcn, :dce, :ce, :notes, true)
                        """, {
                            "fn": d_prenom, "ln": d_nom, "ph": d_tel, "em": d_email,
                            "le": None, "fimo": d_fimo_exp, "dcn": d_carte_num,
                            "dce": d_carte_exp, "ce": d_caces_exp, "notes": d_notes
                        })
                        st.success(f"✅ Chauffeur {d_prenom} {d_nom} ajouté !")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    st.write("### 📋 Liste des Chauffeurs")
    try:
        df_drv_list = load_data("""
            SELECT id, first_name, last_name, phone, email, notes as absences,
                   license_expiry, fimo_fco_expiry, driver_card_expiry
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
                with st.form("edit_driver_form"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        e_prenom = st.text_input("Prénom", value=r['first_name'] or "")
                        e_nom = st.text_input("Nom", value=r['last_name'] or "")
                        e_tel = st.text_input("Téléphone", value=r['phone'] or "")
                        e_email = st.text_input("Email", value=r['email'] or "")
                        e_notes = st.text_area("Absences", value=r['notes'] or "")
                    with ec2:
                        e_fimo = st.date_input("Validité FIMO/FCO", value=r['fimo_fco_expiry'] if pd.notna(r['fimo_fco_expiry']) else datetime.date.today())
                        e_dcnum = st.text_input("N° Carte Conducteur", value=r['driver_card_number'] or "")
                        e_dcexp = st.date_input("Validité Carte Conducteur", value=r['driver_card_expiry'] if pd.notna(r['driver_card_expiry']) else datetime.date.today())
                        e_caces = st.date_input("Validité CACES", value=r['caces_expiry'] if pd.notna(r['caces_expiry']) else datetime.date.today())
                        e_active = st.checkbox("Actif", value=bool(r['is_active']))
                    e_sub = st.form_submit_button("💾 Enregistrer les modifications", type="primary")
                    if e_sub:
                        run_query("""
                            UPDATE drivers SET first_name=:fn, last_name=:ln, phone=:ph, email=:em,
                                fimo_fco_expiry=:fimo, driver_card_number=:dcn, driver_card_expiry=:dce,
                                caces_expiry=:ce, notes=:notes, is_active=:active
                            WHERE id=:id
                        """, {
                            "fn": e_prenom, "ln": e_nom, "ph": e_tel, "em": e_email,
                            "fimo": e_fimo, "dcn": e_dcnum, "dce": e_dcexp, "ce": e_caces,
                            "notes": e_notes, "active": e_active, "id": edit_drv_id
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
                v_ct = st.date_input("Date CT (Contrôle Technique)", value=datetime.date.today() + datetime.timedelta(days=365))
                v_tacho = st.date_input("Chronotachygraphe valide jusqu'au", value=datetime.date.today() + datetime.timedelta(days=365))
                v_limiter = st.date_input("Limiteur de vitesse valide jusqu'au", value=datetime.date.today() + datetime.timedelta(days=365))
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
                        ev_ct = st.date_input("CT valide jusqu'au", value=rv['control_valid_until'] if pd.notna(rv['control_valid_until']) else datetime.date.today())
                        ev_tacho = st.date_input("Chronotachygraphe valide jusqu'au", value=rv['tachograph_valid_until'] if pd.notna(rv['tachograph_valid_until']) else datetime.date.today())
                        ev_limiter = st.date_input("Limiteur valide jusqu'au", value=rv['speed_limiter_valid_until'] if pd.notna(rv['speed_limiter_valid_until']) else datetime.date.today())
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
        df_drv_mobile = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true ORDER BY first_name")
        if df_drv_mobile.empty:
            st.warning("Aucun chauffeur actif.")
            st.stop()

        drv_mobile_dict = dict(zip(df_drv_mobile['id'], df_drv_mobile['first_name'] + " " + df_drv_mobile['last_name']))
        chauffeur_id = st.selectbox("Se connecter en tant que :", options=list(drv_mobile_dict.keys()),
                                     format_func=lambda x: drv_mobile_dict[x])

        today_mobile = datetime.date.today()
        df_assigned = load_data("""
            SELECT o.vehicle_id as truck_id, v.license_plate as truck_label,
                   o.trailer_id as t_id, t.license_plate as trailer_label
            FROM orders o
            LEFT JOIN vehicles v ON o.vehicle_id = v.id
            LEFT JOIN vehicles t ON o.trailer_id = t.id
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
            if pd.notna(row_a['t_id']):
                assigned_trailer_id = row_a['t_id']
                assigned_trailer_label = row_a['trailer_label']

        st.write("### 🚚 Mes Véhicules")
        st.caption("Cliquez pour signaler un problème (usure, casse, saleté...)")

        df_all_veh_m = load_data("SELECT id, license_plate, name, type FROM vehicles WHERE is_available = true")
        veh_dict_m = dict(zip(df_all_veh_m['id'], df_all_veh_m['license_plate'] + " - " + df_all_veh_m['type'] + " (" + df_all_veh_m['name'].fillna('') + ")"))
        keys_list_m = [None] + list(veh_dict_m.keys())

        def issue_form(veh_id, form_key):
            with st.form(form_key):
                final_veh_id = veh_id
                if veh_id is None:
                    final_veh_id = st.selectbox("Véhicule concerné :", options=keys_list_m,
                                                  format_func=lambda x: "--- Choisir un véhicule ---" if x is None else veh_dict_m.get(x, str(x)))
                issue_type = st.selectbox("Type de problème", ["Pneu usé / crevé", "Feu cassé", "Carrosserie endommagée", "Intérieur sale", "Problème moteur / Voyant", "Autre"])
                desc = st.text_area("Explication détaillée", placeholder="Ex: Feu arrière droit brisé en reculant ce matin...")
                photo_file = st.file_uploader("Photo 📸 (optionnelle)", type=["jpg", "jpeg", "png"])
                submitted = st.form_submit_button("Envoyer le signalement 🚀", type="primary", use_container_width=True)
                if submitted:
                    if final_veh_id and desc:
                        photo_path = ""
                        if photo_file is not None:
                            os.makedirs("uploads/photos", exist_ok=True)
                            filename = f"{uuid.uuid4().hex}.jpg"
                            filepath = os.path.join("uploads/photos", filename)
                            with open(filepath, "wb") as f:
                                f.write(photo_file.getbuffer())
                            photo_path = filepath
                        run_query(
                            "INSERT INTO vehicle_issues (driver_id, vehicle_id, description, photo_data) VALUES (:did, :vid, :desc, :pic)",
                            {"did": chauffeur_id, "vid": final_veh_id, "desc": f"[{issue_type}] {desc}", "pic": photo_path}
                        )
                        st.success("✅ Problème signalé !")
                    else:
                        st.error("⚠️ L'explication détaillée et le véhicule sont obligatoires.")

        if assigned_truck_id:
            with st.expander(f"🚛 Camion assigné : {assigned_truck_label}"):
                issue_form(assigned_truck_id, "form_truck")
            if assigned_trailer_label:
                with st.expander(f"🔗 Remorque assignée : {assigned_trailer_label}"):
                    issue_form(assigned_trailer_id, "form_trailer")
        else:
            st.warning("Aucun véhicule assigné automatiquement aujourd'hui dans le planning.")

        with st.expander("🚨 Signaler un problème sur un AUTRE véhicule"):
            issue_form(None, "form_other")

        st.divider()
        st.write("### 📋 Mes missions du jour")
        df_missions = load_data("""
            SELECT o.id, c.name as client, s.address, s.gmaps_link,
                   o.service_type, COALESCE(o.material, o.waste_type) as details,
                   o.requested_slot, o.instructions, o.status
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN sites s ON o.site_id = s.id
            WHERE o.driver_id = :did AND o.requested_date = :d
            ORDER BY o.id
        """, {"did": chauffeur_id, "d": today_mobile})

        if df_missions.empty:
            st.info("Aucune mission pour aujourd'hui.")
        else:
            for _, m in df_missions.iterrows():
                with st.expander(f"📦 {m['client']} — {m['service_type']} ({m['requested_slot']})"):
                    st.write(f"**Adresse :** {m['address']}")
                    if m['gmaps_link']:
                        st.markdown(f"[🗺️ Ouvrir dans Google Maps]({m['gmaps_link']})")
                    st.write(f"**Détails :** {m['details']}")
                    if m['instructions']:
                        st.info(f"ℹ️ {m['instructions']}")

                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        if st.button("✅ LIVRÉ", key=f"done_{m['id']}", use_container_width=True, type="primary"):
                            run_query("UPDATE orders SET status='completed' WHERE id=:id", {"id": m['id']})
                            st.success("Mission validée !")
                            st.cache_data.clear()
                            st.rerun()
                    with col_m2:
                        with st.expander("❌ Signaler un problème"):
                            with st.form(f"mission_issue_{m['id']}"):
                                issue_desc = st.text_area("Décrivez le problème")
                                issue_photo = st.file_uploader("Photo 📸", type=["jpg", "jpeg", "png"], key=f"ph_{m['id']}")
                                if st.form_submit_button("🚨 Envoyer l'alerte au bureau", type="primary", use_container_width=True):
                                    if issue_desc:
                                        pic_path = ""
                                        if issue_photo is not None:
                                            os.makedirs("uploads/photos", exist_ok=True)
                                            filename = f"{uuid.uuid4().hex}.jpg"
                                            filepath = os.path.join("uploads/photos", filename)
                                            with open(filepath, "wb") as f:
                                                f.write(issue_photo.getbuffer())
                                            pic_path = filepath
                                        run_query(
                                            "INSERT INTO order_issues (order_id, driver_id, description, photo_data) VALUES (:oid, :did, :desc, :pic)",
                                            {"oid": m['id'], "did": chauffeur_id, "desc": issue_desc, "pic": pic_path}
                                        )
                                        st.success("🚨 Alerte envoyée au bureau !")
                                    else:
                                        st.error("La description est obligatoire.")
    except Exception as e:
        st.error(f"Erreur : {e}")

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
    pin_input = st.text_input("Code PIN Admin", type="password", max_chars=6)
    pin_ok = False
    if pin_input:
        try:
            df_pin = load_data("SELECT value FROM system_settings WHERE key='admin_pin'")
            stored_pin = df_pin.iloc[0]['value'] if not df_pin.empty else "1234"
            if pin_input == stored_pin:
                pin_ok = True
                st.success("Accès Admin Déverrouillé 🔓")
            else:
                st.error("PIN incorrect.")
        except Exception:
            if pin_input == "1234":
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
    st.write("### 🛒 Catalogue : Matériaux & Déchets")
    tab_mat, tab_waste = st.tabs(["Matériaux (Livraisons)", "Déchets (Bennes)"])
    with tab_mat:
        try:
            df_mat_cat = load_data("SELECT id, name, unit, price_ht FROM catalog_items WHERE category='material' ORDER BY name")
            if df_mat_cat.empty:
                st.info("Aucun matériau dans le catalogue.")
            else:
                st.dataframe(df_mat_cat.drop(columns=['id']), use_container_width=True)
            if pin_ok:
                with st.form("add_material"):
                    m_name = st.text_input("Nom du matériau")
                    m_unit = st.text_input("Unité (ex: tonne, m3)")
                    m_price = st.number_input("Prix HT", min_value=0.0)
                    if st.form_submit_button("➕ Ajouter"):
                        if m_name:
                            run_query("INSERT INTO catalog_items (name, category, unit, price_ht) VALUES (:n, 'material', :u, :p)", {"n": m_name, "u": m_unit, "p": m_price})
                            st.success("Matériau ajouté !")
                            st.cache_data.clear()
                            st.rerun()
        except Exception as e:
            st.error(f"Erreur : {e}")

    with tab_waste:
        try:
            df_waste_cat = load_data("SELECT id, name, unit, price_ht FROM catalog_items WHERE category='waste' ORDER BY name")
            if df_waste_cat.empty:
                st.info("Aucun type de déchet dans le catalogue.")
            else:
                st.dataframe(df_waste_cat.drop(columns=['id']), use_container_width=True)
            if pin_ok:
                with st.form("add_waste"):
                    w_name = st.text_input("Type de déchet")
                    w_unit = st.text_input("Unité")
                    w_price = st.number_input("Prix HT", min_value=0.0, key="w_price")
                    if st.form_submit_button("➕ Ajouter"):
                        if w_name:
                            run_query("INSERT INTO catalog_items (name, category, unit, price_ht) VALUES (:n, 'waste', :u, :p)", {"n": w_name, "u": w_unit, "p": w_price})
                            st.success("Type de déchet ajouté !")
                            st.cache_data.clear()
                            st.rerun()
        except Exception as e:
            st.error(f"Erreur : {e}")

    st.markdown("---")
    st.write("### 📅 Jours de fermeture de l'entreprise")
    st.info("Module en construction 🚧 — Revenez prochainement.")
    try:
        df_closures_view = load_data("SELECT start_date, end_date, reason FROM company_closures ORDER BY start_date")
        if not df_closures_view.empty:
            st.dataframe(df_closures_view, use_container_width=True)
        if pin_ok:
            with st.form("add_closure"):
                cc1, cc2 = st.columns(2)
                with cc1:
                    cl_start = st.date_input("Début de la fermeture")
                    cl_end = st.date_input("Fin de la fermeture")
                with cc2:
                    cl_reason = st.text_input("Motif (ex: Congés annuels)")
                if st.form_submit_button("📅 Ajouter la fermeture"):
                    run_query("INSERT INTO company_closures (start_date, end_date, reason) VALUES (:s, :e, :r)", {"s": cl_start, "e": cl_end, "r": cl_reason})
                    st.success("Fermeture ajoutée !")
                    st.cache_data.clear()
                    st.rerun()
    except Exception as e:
        st.error(f"Erreur fermetures : {e}")
