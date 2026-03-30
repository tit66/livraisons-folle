import streamlit as st
import pandas as pd
import datetime
import hashlib
import uuid
from sqlalchemy import create_engine, text

st.set_page_config(
    page_title="Portail Client — Livraisons Folles",
    page_icon="🚚",
    layout="centered",
)

DB_URI = 'postgresql://n8n:supersecret@n8n-local_postgres_1:5432/n8n'

# ─────────────────────────────────────────────────────────────────────────────
# CONNEXION BDD
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return create_engine(DB_URI)

engine = get_engine()

def run_query(query, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        conn.commit()
        return result

@st.cache_data(ttl=30)
def load_data(query, params=None):
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params or {})

# ─────────────────────────────────────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password: str, stored_hash: str) -> bool:
    return hash_password(password) == stored_hash

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

SLOTS = ["Indifférent dans la journée", "8h Premier tour", "8h-10h", "10h-12h", "13h-15h", "15h-17h"]

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.portail-header {
    background: linear-gradient(135deg, #F9A800, #FFD600);
    color: white;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 2rem;
}
.portail-header h1 { margin: 0; font-size: 2rem; }
.portail-header p { margin: 0.3rem 0 0; opacity: 0.9; }
.commande-card {
    background: #f8f9fa;
    border-left: 4px solid #F9A800;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "client_id" not in st.session_state:
    st.session_state.client_id = None
if "client_name" not in st.session_state:
    st.session_state.client_name = None
if "client_type" not in st.session_state:
    st.session_state.client_type = None
if "portail_page" not in st.session_state:
    st.session_state.portail_page = "login"  # login | register | dashboard | new_order

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="portail-header">
    <h1>🚚 Livraisons Folles</h1>
    <p>Portail Client — Passez commande en ligne</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DÉCONNEXION (si connecté)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.client_id:
    col_name, col_logout = st.columns([8, 2])
    with col_name:
        st.write(f"👋 Connecté en tant que **{st.session_state.client_name}**")
    with col_logout:
        if st.button("🚪 Déconnexion"):
            st.session_state.client_id = None
            st.session_state.client_name = None
            st.session_state.client_type = None
            st.session_state.portail_page = "login"
            st.rerun()
    st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : LOGIN
# ─────────────────────────────────────────────────────────────────────────────
def page_login():
    st.subheader("🔐 Connexion")
    with st.form("login_form"):
        email = st.text_input("Adresse email")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter", type="primary", use_container_width=True)
        if submitted:
            if not email or not password:
                st.error("Email et mot de passe obligatoires.")
            else:
                try:
                    df = load_data(
                        "SELECT id, name, type, password_hash FROM clients WHERE LOWER(email) = LOWER(:email)",
                        {"email": email}
                    )
                    if df.empty:
                        st.error("Aucun compte trouvé avec cet email.")
                    elif not df.iloc[0]["password_hash"]:
                        st.error("Ce compte n'a pas encore de mot de passe. Contactez-nous.")
                    elif not check_password(password, df.iloc[0]["password_hash"]):
                        st.error("Mot de passe incorrect.")
                    else:
                        st.session_state.client_id = df.iloc[0]["id"]
                        st.session_state.client_name = df.iloc[0]["name"]
                        st.session_state.client_type = df.iloc[0]["type"]
                        st.session_state.portail_page = "dashboard"
                        st.cache_data.clear()
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Pas encore de compte ?")
        if st.button("✍️ Créer un compte", use_container_width=True):
            st.session_state.portail_page = "register"
            st.rerun()
    with col2:
        st.write("Mot de passe oublié ?")
        if st.button("📧 Réinitialiser", use_container_width=True):
            st.session_state.portail_page = "reset"
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : INSCRIPTION
# ─────────────────────────────────────────────────────────────────────────────
def page_register():
    st.subheader("✍️ Créer un compte")
    client_type = st.radio("Je suis :", ["Professionnel", "Particulier"], horizontal=True)
    st.markdown("---")

    with st.form("register_form"):
        if client_type == "Professionnel":
            st.write("#### 🏢 Informations de l'entreprise")
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Raison sociale *")
                siret = st.text_input("SIRET")
                email = st.text_input("Email *")
            with c2:
                phone = st.text_input("Téléphone *")
                billing_address = st.text_area("Adresse de facturation")

            st.write("#### 📍 Premier chantier (optionnel)")
            c3, c4 = st.columns(2)
            with c3:
                site_label = st.text_input("Nom du chantier (ex: Chantier Maison Dupont)")
                site_address = st.text_area("Adresse du chantier")
            with c4:
                site_gmaps = st.text_input("Lien Google Maps")
                st.caption("Google Maps → Partager → Copier le lien")

        else:  # Particulier
            st.write("#### 👤 Vos informations")
            c1, c2 = st.columns(2)
            with c1:
                prenom = st.text_input("Prénom *")
                nom = st.text_input("Nom *")
                email = st.text_input("Email *")
            with c2:
                phone = st.text_input("Téléphone *")
                billing_address = st.text_area("Adresse (livraison par défaut)")
            name = None
            siret = None
            site_label = site_address = site_gmaps = ""

        st.markdown("---")
        st.write("#### 🔑 Mot de passe")
        c5, c6 = st.columns(2)
        with c5:
            password = st.text_input("Mot de passe *", type="password")
        with c6:
            password2 = st.text_input("Confirmer le mot de passe *", type="password")

        submitted = st.form_submit_button("✅ Créer mon compte", type="primary", use_container_width=True)

        if submitted:
            # Construire le nom final
            if client_type == "Particulier":
                name = f"{prenom} {nom}".strip()

            # Validations
            errors = []
            if not name:
                errors.append("Le nom / raison sociale est obligatoire.")
            if not email:
                errors.append("L'email est obligatoire.")
            if not phone:
                errors.append("Le téléphone est obligatoire.")
            if not password:
                errors.append("Le mot de passe est obligatoire.")
            elif len(password) < 6:
                errors.append("Le mot de passe doit faire au moins 6 caractères.")
            elif password != password2:
                errors.append("Les mots de passe ne correspondent pas.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                try:
                    # Vérifier email unique
                    df_exist = load_data(
                        "SELECT id FROM clients WHERE LOWER(email) = LOWER(:email)",
                        {"email": email}
                    )
                    if not df_exist.empty:
                        st.error("Un compte existe déjà avec cet email.")
                    else:
                        pw_hash = hash_password(password)
                        type_db = "Professionnel" if client_type == "Professionnel" else "Particulier"

                        res = run_query("""
                            INSERT INTO clients (name, type, email, phone, billing_address, siret, password_hash)
                            VALUES (:name, :type, :email, :phone, :addr, :siret, :pw)
                            RETURNING id
                        """, {
                            "name": name, "type": type_db, "email": email,
                            "phone": phone, "addr": billing_address,
                            "siret": siret or None, "pw": pw_hash
                        }).fetchone()
                        client_id = res[0]

                        # Créer le premier chantier si renseigné
                        if site_address or billing_address:
                            addr = site_address if site_address else billing_address
                            lbl = site_label if site_label else ("Adresse principale" if client_type == "Particulier" else "Chantier principal")
                            run_query("""
                                INSERT INTO sites (client_id, label, address, gmaps_link, is_active)
                                VALUES (:cid, :lbl, :addr, :gmaps, true)
                            """, {"cid": client_id, "lbl": lbl, "addr": addr, "gmaps": site_gmaps or None})

                        st.session_state.client_id = client_id
                        st.session_state.client_name = name
                        st.session_state.client_type = type_db
                        st.session_state.portail_page = "dashboard"
                        st.cache_data.clear()
                        st.success(f"✅ Compte créé ! Bienvenue {name} 👋")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de la création : {e}")

    st.markdown("---")
    if st.button("← Retour à la connexion"):
        st.session_state.portail_page = "login"
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : DASHBOARD CLIENT
# ─────────────────────────────────────────────────────────────────────────────
def page_dashboard():
    client_id = st.session_state.client_id
    client_type = st.session_state.client_type

    col_title, col_btn = st.columns([7, 3])
    with col_title:
        st.subheader("📋 Mes commandes")
    with col_btn:
        if st.button("➕ Nouvelle commande", type="primary", use_container_width=True):
            st.session_state.portail_page = "new_order"
            st.rerun()

    # Historique commandes
    try:
        df_orders = load_data("""
            SELECT o.id, o.service_type,
                   COALESCE(o.material, o.waste_type) as details,
                   o.container_type,
                   o.requested_date, o.requested_slot,
                   o.status, o.instructions,
                   s.address as chantier,
                   s.label as chantier_label
            FROM orders o
            LEFT JOIN sites s ON o.site_id = s.id
            WHERE o.client_id = :cid
            ORDER BY o.created_at DESC
            LIMIT 20
        """, {"cid": client_id})

        STATUS_LABELS = {
            "pending":    "🕐 En attente",
            "planned":    "📋 Planifiée",
            "dispatched": "🚚 En route",
            "done":       "✅ Terminée",
            "cancelled":  "❌ Annulée",
        }

        if df_orders.empty:
            st.info("Aucune commande pour l'instant. Cliquez sur **➕ Nouvelle commande** pour démarrer.")
        else:
            for _, row in df_orders.iterrows():
                status_label = STATUS_LABELS.get(row["status"], row["status"])
                date_str = row["requested_date"].strftime("%d/%m/%Y") if pd.notna(row["requested_date"]) else "?"
                details_str = f" — {row['details']}" if row["details"] else ""
                container_str = f" ({row['container_type']})" if row["container_type"] else ""
                chantier_str = row["chantier_label"] or row["chantier"] or ""

                with st.expander(f"{status_label} — {row['service_type']}{details_str}{container_str} — {date_str}"):
                    st.write(f"**Chantier :** {chantier_str}")
                    st.write(f"**Adresse :** {row['chantier'] or '—'}")
                    st.write(f"**Créneau :** {row['requested_slot'] or '—'}")
                    if row["instructions"]:
                        st.info(f"💬 {row['instructions']}")
    except Exception as e:
        st.error(f"Erreur : {e}")

    st.markdown("---")

    # Gestion des chantiers (Pro seulement)
    if client_type == "Professionnel":
        with st.expander("📍 Mes chantiers / adresses"):
            try:
                df_sites = load_data(
                    "SELECT id, label, address, gmaps_link, is_active FROM sites WHERE client_id = :cid ORDER BY label",
                    {"cid": client_id}
                )
                if df_sites.empty:
                    st.info("Aucun chantier enregistré.")
                else:
                    for _, s in df_sites.iterrows():
                        active = "✅" if s["is_active"] else "⏸️"
                        st.write(f"{active} **{s['label']}** — {s['address']}")

                st.markdown("---")
                st.write("**Ajouter un chantier :**")
                with st.form("add_site_form"):
                    ns_label = st.text_input("Nom du chantier")
                    ns_address = st.text_area("Adresse exacte *")
                    ns_gmaps = st.text_input("Lien Google Maps (optionnel)")
                    if st.form_submit_button("➕ Ajouter"):
                        if ns_address:
                            lbl = ns_label or "Nouveau chantier"
                            run_query("""
                                INSERT INTO sites (client_id, label, address, gmaps_link, is_active)
                                VALUES (:cid, :lbl, :addr, :gmaps, true)
                            """, {"cid": client_id, "lbl": lbl, "addr": ns_address, "gmaps": ns_gmaps or None})
                            st.success(f"✅ Chantier '{lbl}' ajouté !")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("L'adresse est obligatoire.")
            except Exception as e:
                st.error(f"Erreur chantiers : {e}")

    # Modification compte
    with st.expander("⚙️ Mon compte"):
        try:
            df_me = load_data("SELECT name, email, phone, billing_address FROM clients WHERE id = :id", {"id": client_id})
            r = df_me.iloc[0]
            with st.form("edit_account_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_phone = st.text_input("Téléphone", value=r["phone"] or "")
                    new_email = st.text_input("Email", value=r["email"] or "")
                with c2:
                    new_addr = st.text_area("Adresse de facturation", value=r["billing_address"] or "")
                st.write("**Changer le mot de passe** (laisser vide pour ne pas changer)")
                c3, c4 = st.columns(2)
                with c3:
                    new_pw = st.text_input("Nouveau mot de passe", type="password")
                with c4:
                    new_pw2 = st.text_input("Confirmer", type="password")
                if st.form_submit_button("💾 Enregistrer"):
                    if new_pw and new_pw != new_pw2:
                        st.error("Les mots de passe ne correspondent pas.")
                    else:
                        pw_hash = hash_password(new_pw) if new_pw else None
                        if pw_hash:
                            run_query(
                                "UPDATE clients SET phone=:ph, email=:em, billing_address=:addr, password_hash=:pw WHERE id=:id",
                                {"ph": new_phone, "em": new_email, "addr": new_addr, "pw": pw_hash, "id": client_id}
                            )
                        else:
                            run_query(
                                "UPDATE clients SET phone=:ph, email=:em, billing_address=:addr WHERE id=:id",
                                {"ph": new_phone, "em": new_email, "addr": new_addr, "id": client_id}
                            )
                        st.success("✅ Compte mis à jour.")
                        st.cache_data.clear()
        except Exception as e:
            st.error(f"Erreur compte : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : NOUVELLE COMMANDE
# ─────────────────────────────────────────────────────────────────────────────
def page_new_order():
    client_id = st.session_state.client_id
    client_type = st.session_state.client_type

    if st.button("← Retour à mes commandes"):
        st.session_state.portail_page = "dashboard"
        st.rerun()

    st.subheader("➕ Nouvelle commande")

    # ── Chantier ──
    st.write("### 1️⃣ Chantier / Adresse de livraison")
    if client_type == "Professionnel":
        df_sites = load_data(
            "SELECT id, label, address FROM sites WHERE client_id = :cid AND is_active = true ORDER BY label",
            {"cid": client_id}
        )
        site_dict = {}
        for _, s in df_sites.iterrows():
            site_dict[s["id"]] = f"{s['label']} — {s['address']}"
        site_dict["NEW"] = "➕ Nouvelle adresse / chantier"

        selected_site = st.selectbox(
            "Chantier",
            options=[None] + list(site_dict.keys()),
            format_func=lambda x: "--- Choisir un chantier ---" if x is None else site_dict.get(x, "")
        )
        new_site_label = new_site_address = new_site_gmaps = ""
        if selected_site == "NEW":
            c1, c2 = st.columns(2)
            with c1:
                new_site_label = st.text_input("Nom du chantier")
                new_site_address = st.text_area("Adresse *")
            with c2:
                new_site_gmaps = st.text_input("Lien Google Maps")
    else:
        # Particulier : utilise son adresse ou en saisit une nouvelle
        df_me = load_data("SELECT billing_address FROM clients WHERE id = :id", {"id": client_id})
        default_addr = df_me.iloc[0]["billing_address"] if not df_me.empty else ""
        df_sites_part = load_data(
            "SELECT id, label, address FROM sites WHERE client_id = :cid AND is_active = true ORDER BY label",
            {"cid": client_id}
        )
        site_dict = {}
        if default_addr:
            site_dict["BILLING"] = f"Mon adresse : {default_addr}"
        for _, s in df_sites_part.iterrows():
            site_dict[s["id"]] = f"{s['label']} — {s['address']}"
        site_dict["NEW"] = "➕ Autre adresse"

        selected_site = st.selectbox(
            "Adresse de livraison",
            options=[None] + list(site_dict.keys()),
            format_func=lambda x: "--- Choisir ---" if x is None else site_dict.get(x, "")
        )
        new_site_label = new_site_address = new_site_gmaps = ""
        if selected_site == "NEW":
            new_site_address = st.text_area("Adresse de livraison *")

    st.divider()

    # ── Type de prestation ──
    st.write("### 2️⃣ Type de prestation")
    df_stype = load_data("SELECT name FROM catalog_items WHERE category='service_type' ORDER BY name")
    service_options = df_stype['name'].tolist() if not df_stype.empty else ["Livraison de matériaux", "Location de benne"]
    prestation = st.radio("Prestation souhaitée", service_options, horizontal=True)

    is_benne = any(x in str(prestation).lower() for x in ["benne", "pose", "retrait", "rotation", "enlèvement"])

    st.divider()

    # ── Détails de la commande ──
    st.write("### 3️⃣ Détails")
    marchandise = volume_benne = type_benne = action_benne = None
    quantite = 1.0
    loading_point_val = unloading_point_val = ""

    if not is_benne:
        df_mat = load_data("SELECT name FROM catalog_items WHERE category='material' ORDER BY name")
        mat_opts = df_mat['name'].tolist() if not df_mat.empty else []
        if "Big Bag" not in mat_opts:
            mat_opts = mat_opts + ["Big Bag"]
        if mat_opts:
            marchandise = st.selectbox("Matériau", mat_opts)
        else:
            marchandise = st.text_input("Matériau")
        quantite = st.number_input("Quantité (tonnes)", min_value=0.5, step=0.5, value=1.0)

        df_load_pts = load_data("SELECT name FROM catalog_items WHERE category='loading_point' ORDER BY name")
        load_opts = df_load_pts['name'].tolist() if not df_load_pts.empty else []
        if load_opts:
            loading_point_val = st.selectbox("📍 Lieu de chargement", load_opts)
        else:
            loading_point_val = st.text_input("📍 Lieu de chargement")
    else:
        action_benne = st.radio("Action", ["Pose", "Rotation", "Enlèvement", "Déplacement"], horizontal=True)
        df_waste = load_data("SELECT name FROM catalog_items WHERE category='waste' ORDER BY name")
        waste_opts = df_waste['name'].tolist() if not df_waste.empty else []
        if waste_opts:
            type_benne = st.selectbox("Type de déchets", waste_opts)
        else:
            type_benne = st.text_input("Type de déchets")

        df_inv = load_data("SELECT size FROM skip_inventory ORDER BY size")
        inv_opts = df_inv['size'].tolist() if not df_inv.empty else []
        if inv_opts:
            volume_benne = st.selectbox("Volume de benne", inv_opts)
        else:
            volume_benne = st.text_input("Volume de benne")

        if type_benne and "gravat" in str(type_benne).lower():
            st.warning("⚠️ Pour les gravats, le volume maximum conseillé est de 10m³")

        df_unload = load_data("SELECT name FROM catalog_items WHERE category='unloading_point' ORDER BY name")
        unload_opts = df_unload['name'].tolist() if not df_unload.empty else []
        if unload_opts:
            unloading_point_val = st.selectbox("📍 Point de déchargement", unload_opts)
        else:
            unloading_point_val = st.text_input("📍 Point de déchargement")

    st.divider()

    # ── Date & créneau ──
    st.write("### 4️⃣ Date & créneau souhaités")
    date_livraison = st.date_input(
        "Date souhaitée",
        value=datetime.date.today() + datetime.timedelta(days=1),
        format="DD/MM/YYYY"
    )
    est_valide, msg_valide = est_jour_ouvrable(date_livraison)
    if not est_valide:
        st.error(msg_valide)
    else:
        st.success(msg_valide)

    creneau = st.selectbox("⏰ Créneau préféré", SLOTS)
    instructions = st.text_area("💬 Instructions particulières (accès, contact sur place, code portail…)")

    souhaite_devis = st.checkbox("📄 Je souhaite recevoir un devis avant la prestation")

    st.divider()

    # ── Validation ──
    if st.button("✅ Envoyer ma demande", type="primary", use_container_width=True, disabled=not est_valide):
        try:
            final_site_id = None

            if client_type == "Professionnel":
                if selected_site == "NEW":
                    if not new_site_address:
                        st.error("L'adresse est obligatoire.")
                        st.stop()
                    lbl = new_site_label or "Nouveau chantier"
                    res = run_query("""
                        INSERT INTO sites (client_id, label, address, gmaps_link, is_active)
                        VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id
                    """, {"cid": client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps or None}).fetchone()
                    final_site_id = res[0]
                elif selected_site and selected_site != "BILLING":
                    final_site_id = selected_site
            else:
                if selected_site == "NEW":
                    if not new_site_address:
                        st.error("L'adresse est obligatoire.")
                        st.stop()
                    res = run_query("""
                        INSERT INTO sites (client_id, label, address, is_active)
                        VALUES (:cid, 'Adresse livraison', :addr, true) RETURNING id
                    """, {"cid": client_id, "addr": new_site_address}).fetchone()
                    final_site_id = res[0]
                elif selected_site and selected_site != "BILLING":
                    final_site_id = selected_site
                else:
                    # Utiliser l'adresse de facturation → créer un site temporaire
                    df_me2 = load_data("SELECT billing_address FROM clients WHERE id = :id", {"id": client_id})
                    addr_billing = df_me2.iloc[0]["billing_address"] if not df_me2.empty else ""
                    if addr_billing:
                        res = run_query("""
                            INSERT INTO sites (client_id, label, address, is_active)
                            VALUES (:cid, 'Adresse principale', :addr, true) RETURNING id
                        """, {"cid": client_id, "addr": addr_billing}).fetchone()
                        final_site_id = res[0]

            if not final_site_id and not selected_site:
                st.error("Veuillez sélectionner ou saisir une adresse de livraison.")
                st.stop()

            service_final = f"Benne - {action_benne}" if is_benne else prestation
            initial_status = "pending" if not souhaite_devis else "pending"
            instr_final = (instructions or "")
            if souhaite_devis:
                instr_final = "[DEVIS DEMANDÉ] " + instr_final

            run_query("""
                INSERT INTO orders (
                    client_id, site_id, service_type, material, quantity_tons,
                    container_type, waste_type, instructions, status, source,
                    requested_date, requested_slot, loading_point, unloading_point,
                    quote_requested
                ) VALUES (
                    :client_id, :site_id, :service_type, :material, :quantity,
                    :container_type, :waste_type, :instructions, :status, 'portail_client',
                    :req_date, :req_slot, :lp, :up, :devis
                )
            """, {
                "client_id": client_id,
                "site_id": final_site_id,
                "service_type": service_final,
                "material": marchandise,
                "quantity": quantite if not is_benne else None,
                "container_type": volume_benne,
                "waste_type": type_benne,
                "instructions": instr_final,
                "status": initial_status,
                "req_date": date_livraison,
                "req_slot": creneau,
                "lp": loading_point_val or None,
                "up": unloading_point_val or None,
                "devis": souhaite_devis,
            })
            st.cache_data.clear()
            st.success("🎉 Votre demande a bien été envoyée ! Nous vous contacterons rapidement pour confirmation.")
            st.balloons()
            # Retour au dashboard après 2s
            import time
            time.sleep(2)
            st.session_state.portail_page = "dashboard"
            st.rerun()

        except Exception as e:
            st.error(f"Erreur lors de l'envoi : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : RESET MOT DE PASSE
# ─────────────────────────────────────────────────────────────────────────────
def send_reset_email(to_email: str, to_name: str, temp_pw: str) -> bool:
    """Envoie le mot de passe temporaire par email via Gmail SMTP."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    SMTP_USER = "smllivraisons@gmail.com"
    SMTP_PASS = "sncerbwvitfiqtjq"
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    subject = "🔑 Réinitialisation de votre mot de passe — Livraisons Folles"
    body = f"""Bonjour {to_name},

Votre mot de passe temporaire est : {temp_pw}

Connectez-vous avec ce code sur le portail client, puis changez-le immédiatement
dans la rubrique ⚙️ Mon compte.

Si vous n'êtes pas à l'origine de cette demande, ignorez cet email — votre
mot de passe actuel reste inchangé.

— L'équipe Livraisons Folles
"""
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Erreur envoi email : {e}")
        return False


def page_reset():
    st.subheader("📧 Réinitialisation du mot de passe")
    st.info("Entrez votre email. Si un compte existe, un nouveau mot de passe temporaire vous sera **envoyé par email**.")
    with st.form("reset_form"):
        email = st.text_input("Votre adresse email")
        submitted = st.form_submit_button("Envoyer", type="primary", use_container_width=True)
        if submitted and email:
            df = load_data(
                "SELECT id, name FROM clients WHERE LOWER(email) = LOWER(:email)",
                {"email": email}
            )
            # Réponse volontairement identique que le compte existe ou non (anti-enumération)
            if df.empty:
                st.success("✅ Si un compte existe avec cet email, vous recevrez un mot de passe temporaire dans quelques minutes.")
            else:
                import random, string
                temp_pw = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                run_query(
                    "UPDATE clients SET password_hash=:pw WHERE id=:id",
                    {"pw": hash_password(temp_pw), "id": df.iloc[0]["id"]}
                )
                sent = send_reset_email(email, df.iloc[0]["name"], temp_pw)
                if sent:
                    st.success("✅ Un mot de passe temporaire vous a été envoyé par email.")
                # En cas d'échec d'envoi, on ne révèle pas le code à l'écran
    if st.button("← Retour"):
        st.session_state.portail_page = "login"
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ROUTEUR
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.client_id:
    if st.session_state.portail_page == "register":
        page_register()
    elif st.session_state.portail_page == "reset":
        page_reset()
    else:
        page_login()
else:
    if st.session_state.portail_page == "new_order":
        page_new_order()
    else:
        page_dashboard()
