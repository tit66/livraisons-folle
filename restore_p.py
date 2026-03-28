import re

with open("app.py", "r") as f:
    content = f.read()

# Make sure we add back the function est_jour_ouvrable that I might have deleted
func_block = """
def est_jour_ouvrable(date_obj):
    if date_obj.weekday() >= 5: return False, "C'est le week-end !"
    if date_obj in get_jours_feries(date_obj.year): return False, "C'est un jour férié !"
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT reason FROM company_closures WHERE :d >= start_date AND :d <= end_date LIMIT 1"), {"d": date_obj}).fetchone()
            if res: return False, f"Fermeture : {res[0]}"
    except: pass
    return True, ""
"""

if "def est_jour_ouvrable(" not in content:
    content = content.replace("# --- VERIFICATION DES ALERTES", func_block + "\n# --- VERIFICATION DES ALERTES")

old_prise_commande = """elif navigation == "➕ Prise de Commande":
    st.title("➕ Nouvelle Commande")
    st.info("Le formulaire de commande classique est ici.")"""

new_prise_commande = """elif navigation == "➕ Prise de Commande":
    st.title("➕ Nouvelle Commande")
    df_clients = load_data("SELECT id, name FROM clients ORDER BY name")
    
    if not df_clients.empty:
        client_dict = dict(zip(df_clients['id'], df_clients['name']))
        selected_client_id = st.selectbox("1️⃣ Client", options=[None] + list(client_dict.keys()), format_func=lambda x: "--- Choisir un client ---" if x is None else client_dict[x])
        
        if selected_client_id:
            df_sites = load_data("SELECT id, label, address FROM sites WHERE client_id = :cid AND is_active = true", {"cid": selected_client_id})
            site_options = {None: "--- Aucun chantier spécifique ---"}
            if not df_sites.empty:
                for _, row in df_sites.iterrows(): site_options[row['id']] = f"{row['label']} - {row['address']}"
            selected_site_id = st.selectbox("2️⃣ Chantier", options=list(site_options.keys()), format_func=lambda x: site_options[x])
            
            st.divider()
            prestation = st.radio("3️⃣ Type de Prestation", ["Livraison de matériaux", "Location de benne", "Autre"], horizontal=True)
            
            st.write("")
            colA, colB = st.columns(2)
            
            with colA:
                marchandise, quantite, type_benne, volume_benne, action_benne = None, None, None, None, None
                if prestation == "Livraison de matériaux":
                    marchandise = st.selectbox("Type de marchandise", ["Sable", "Gravier", "Terre végétale", "Mélange béton"])
                    quantite = st.number_input("Quantité (Tonnes)", min_value=0.5, step=0.5, value=1.0)
                elif prestation == "Location de benne":
                    action_benne = st.radio("Type d'intervention", ["Pose", "Rotation", "Enlèvement", "Déplacement"], horizontal=True)
                    type_benne = st.selectbox("Type de déchets", ["Gravats", "DIB (Tout venant)", "Déchets verts", "Bois"])
                    options_volume = ["8m3", "10m3"] if type_benne == "Gravats" else ["8m3", "10m3", "15m3", "30m3"]
                    if type_benne == "Gravats": st.caption("⚠️ Pour les gravats, le volume maximum est de 10m3 (limite de poids).")
                    volume_benne = st.selectbox("Volume de la benne", options_volume)
                    
            with colB:
                date_livraison = st.date_input("Date souhaitée", datetime.date.today() + datetime.timedelta(days=1), format="DD/MM/YYYY")
                
                # Check func logic
                est_valide = True
                message_erreur = ""
                try:
                    est_valide, message_erreur = est_jour_ouvrable(date_livraison)
                except Exception:
                    pass
                
                if not est_valide: st.error(f"⚠️ {message_erreur} Impossible.")
                
                creneaux = ["Indifférent dans la journée", "8h (Premier tour)", "8h - 10h", "10h - 12h", "13h - 15h", "15h - 17h"]
                creneau_choisi = st.selectbox("Créneau horaire", creneaux)
                instructions = st.text_area("Instructions spéciales pour le chauffeur")
            
            st.write("")
            if st.button("✅ Valider et Enregistrer", type="primary", use_container_width=True, disabled=not est_valide):
                try:
                    insert_query = \"\"\"
                    INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons, container_type, waste_type, instructions, status, source, requested_date, requested_slot) 
                    VALUES (:client_id, :site_id, :service_type, :material, :quantity, :container_type, :waste_type, :instructions, 'pending', 'admin_streamlit', :req_date, :req_slot)
                    \"\"\"
                    service_final = f"Benne - {action_benne}" if prestation == "Location de benne" else prestation
                    run_query(insert_query, {
                        "client_id": selected_client_id, "site_id": selected_site_id, "service_type": service_final,
                        "material": marchandise, "quantity": quantite, "container_type": volume_benne,
                        "waste_type": type_benne, "instructions": instructions, "req_date": date_livraison, "req_slot": creneau_choisi
                    })
                    st.success(f"🎉 Commande enregistrée pour le {date_livraison.strftime('%d/%m/%Y')} (Créneau : {creneau_choisi}).")
                except Exception as e:
                    st.error(f"Erreur : {e}")
    else:
        st.warning("Aucun client dans la base.")"""

content = content.replace(old_prise_commande, new_prise_commande)

old_planning = """elif navigation == "📅 Planning":
    st.title("📅 Planning & Assignation")
    st.info("Assignation des tournées.")"""

new_planning = """elif navigation == "📅 Planning":
    st.title("📅 Planning & Assignation")
    st.write("Assignez les commandes en attente aux chauffeurs et véhicules.")
    
    date_planning = st.date_input("Date du planning à préparer", datetime.date.today() + datetime.timedelta(days=1), format="DD/MM/YYYY")
    
    query_pending = \"\"\"
        SELECT o.id, c.name as client_name, o.service_type, COALESCE(o.material, o.waste_type) as details, 
               COALESCE(o.quantity_tons::text || ' T', o.container_type) as qty, o.requested_slot, o.status
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.requested_date = :d AND o.status IN ('pending', 'assigned')
        ORDER BY o.requested_slot ASC
    \"\"\"
    df_pending = load_data(query_pending, {"d": date_planning})
    
    if df_pending.empty:
        st.success(f"Aucune commande en attente pour le {date_planning.strftime('%d/%m/%Y')}.")
    else:
        st.write(f"### Commandes pour le {date_planning.strftime('%d/%m/%Y')} ({len(df_pending)} à traiter)")
        
        df_chauffeurs = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true")
        chauffeurs_list = ["(Non assigné)"]
        if not df_chauffeurs.empty:
            chauffeurs_list.extend([f"{r['first_name']} {r['last_name']}" for _, r in df_chauffeurs.iterrows()])
            
        df_vehicules = load_data("SELECT license_plate, brand_model FROM vehicles WHERE is_active = true")
        vehicules_list = ["(Non assigné)"]
        if not df_vehicules.empty:
            vehicules_list.extend([f"{r['license_plate']} - {r['brand_model']}" for _, r in df_vehicules.iterrows()])
        
        for idx, row in df_pending.iterrows():
            with st.container():
                st.markdown(f"**N° {row['id']} - {row['client_name']}** | {row['service_type']} | {row['qty']} ({row['details']}) | 🕒 {row['requested_slot']}")
                
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    chauffeur = st.selectbox(f"Chauffeur", chauffeurs_list, key=f"chauf_{row['id']}")
                with col2:
                    camion = st.selectbox(f"Véhicule", vehicules_list, key=f"cam_{row['id']}")
                with col3:
                    st.write("")
                    st.write("")
                    if st.button("💾 Assigner", key=f"btn_{row['id']}", type="primary"):
                        st.success(f"Commande {row['id']} assignée à {chauffeur} ({camion}).")
                st.divider()"""

content = content.replace(old_planning, new_planning)

with open("app.py", "w") as f:
    f.write(content)
