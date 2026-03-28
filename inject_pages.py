import re

with open("app.py", "r") as f:
    content = f.read()

chauffeurs_code = """
elif navigation == "👥 Chauffeurs":
    st.title("👥 Gestion des Chauffeurs")
    
    st.write("### ➕ Ajouter un Chauffeur")
    with st.expander("Ouvrir le formulaire d'ajout"):
        with st.form("add_driver_form"):
            col1, col2 = st.columns(2)
            with col1:
                f_name = st.text_input("Prénom *")
                l_name = st.text_input("Nom *")
                phone = st.text_input("Téléphone")
                email = st.text_input("Email")
                absence = st.text_input("Période d'absence (ex: Congés du 12 au 20 Août)")
            with col2:
                num_permis = st.text_input("N° de Permis de Conduire")
                # Types de permis en checkbox (on stocke sous forme de chaîne simple pour ce MVP ou on ignore)
                st.write("Types de Permis")
                c_b = st.checkbox("B")
                c_be = st.checkbox("BE")
                c_c = st.checkbox("C")
                c_ce = st.checkbox("CE")
                
                st.write("CACES / Habilitations")
                caces_grue = st.checkbox("CACES Grue Auxiliaire")
                caces_chariot = st.checkbox("CACES Chariot")
                
            col3, col4 = st.columns(2)
            with col3:
                date_permis = st.date_input("Validité du Permis *")
                date_fco = st.date_input("Validité FIMO / FCO *")
            with col4:
                num_carte = st.text_input("N° Carte Conducteur")
                date_carte = st.date_input("Validité Carte Conducteur *")
                date_caces = st.date_input("Validité CACES (général)")
                
            if st.form_submit_button("✅ Ajouter le chauffeur", type="primary"):
                if f_name and l_name:
                    permis_list = []
                    if c_b: permis_list.append('B')
                    if c_be: permis_list.append('BE')
                    if c_c: permis_list.append('C')
                    if c_ce: permis_list.append('CE')
                    
                    caces_list = []
                    if caces_grue: caces_list.append('Grue')
                    if caces_chariot: caces_list.append('Chariot')
                    
                    notes = absence if absence else ""
                    if caces_list:
                        notes += " | CACES: " + ", ".join(caces_list)
                        
                    run_query(\"\"\"
                        INSERT INTO drivers (first_name, last_name, phone, email, license_expiry, fimo_fco_expiry, driver_card_number, driver_card_expiry, caces_expiry, is_active, notes)
                        VALUES (:f, :l, :p, :e, :le, :fimo, :dcn, :dce, :cac, true, :notes)
                    \"\"\", {
                        "f": f_name, "l": l_name, "p": phone, "e": email, 
                        "le": date_permis, "fimo": date_fco, "dcn": num_carte, "dce": date_carte, "cac": date_caces, "notes": notes
                    })
                    st.success("Chauffeur ajouté !")
                    st.rerun()
                else:
                    st.error("Le nom et prénom sont obligatoires.")
                    
    st.write("### 📋 Liste des Chauffeurs")
    df_d = load_data("SELECT id, first_name, last_name, phone, email, notes as absences, license_expiry, fimo_fco_expiry, driver_card_expiry FROM drivers ORDER BY first_name")
    if not df_d.empty:
        df_d.columns = ["ID", "Prénom", "Nom", "Téléphone", "Email", "Absences / Notes", "Fin Permis", "Fin FCO", "Fin Carte"]
        st.dataframe(df_d, use_container_width=True, hide_index=True)
        
        st.write("### ✏️ Éditer / Supprimer un chauffeur")
        d_dict = dict(zip(df_d['ID'], df_d['Prénom'] + " " + df_d['Nom']))
        edit_id = st.selectbox("Choisir un chauffeur", options=[None] + list(d_dict.keys()), format_func=lambda x: "---" if x is None else d_dict[x])
        if edit_id:
            row = load_data(f"SELECT * FROM drivers WHERE id = '{edit_id}'").iloc[0]
            with st.form("edit_d"):
                st.write(f"Modification de {row['first_name']} {row['last_name']}")
                new_abs = st.text_input("Absences / Notes", value=row['notes'] if row['notes'] else "")
                new_le = st.date_input("Fin Permis", value=row['license_expiry'])
                new_fimo = st.date_input("Fin FCO", value=row['fimo_fco_expiry'])
                new_carte = st.date_input("Fin Carte Cond.", value=row['driver_card_expiry'])
                is_active = st.checkbox("Actif", value=bool(row['is_active']))
                if st.form_submit_button("💾 Mettre à jour"):
                    run_query("UPDATE drivers SET notes=:n, license_expiry=:le, fimo_fco_expiry=:fimo, driver_card_expiry=:dc, is_active=:a WHERE id=:id",
                              {"n": new_abs, "le": new_le, "fimo": new_fimo, "dc": new_carte, "a": is_active, "id": edit_id})
                    st.success("Mis à jour !")
                    st.rerun()

elif navigation == "🚚 Flotte":
    st.title("🚚 Gestion de la Flotte")
    
    st.write("### ➕ Ajouter un Véhicule")
    with st.expander("Ouvrir le formulaire d'ajout"):
        with st.form("add_veh"):
            col1, col2 = st.columns(2)
            with col1:
                v_type = st.selectbox("Type", ["Camion", "Tracteur", "Remorque", "Semi-remorque"])
                v_name = st.text_input("Nom personnalisé / Réf interne")
                brand = st.text_input("Marque")
                model = st.text_input("Modèle")
                plate = st.text_input("Immatriculation *")
                is_remorqueur = st.checkbox("Ce véhicule est remorqueur (attelage)")
            with col2:
                st.write("Validités")
                ct_date = st.date_input("Date limite Contrôle Technique *")
                # Uniquement pour véhicules à moteur
                chrono_date = st.date_input("Date limite Chronotachygraphe (Si applicable)")
                limiteur_date = st.date_input("Date limite Limiteur de vitesse (Si applicable)")
                
            if st.form_submit_button("✅ Ajouter le véhicule", type="primary"):
                if plate:
                    run_query(\"\"\"
                        INSERT INTO vehicles (name, brand, model, license_plate, type, control_valid_until, tachograph_valid_until, speed_limiter_valid_until, is_available, maintenance_notes)
                        VALUES (:n, :b, :m, :lp, :t, :ct, :c, :l, true, :notes)
                    \"\"\", {
                        "n": v_name, "b": brand, "m": model, "lp": plate, "t": v_type, 
                        "ct": ct_date, "c": chrono_date if v_type in ["Camion", "Tracteur"] else None, 
                        "l": limiteur_date if v_type in ["Camion", "Tracteur"] else None,
                        "notes": "Remorqueur" if is_remorqueur else ""
                    })
                    st.success("Véhicule ajouté !")
                    st.rerun()
                else:
                    st.error("L'immatriculation est obligatoire.")
                    
    st.write("### 📋 Liste de la Flotte")
    tabs = st.tabs(["Camions", "Tracteurs", "Remorques", "Semi-remorques"])
    
    for i, t in enumerate(["Camion", "Tracteur", "Remorque", "Semi-remorque"]):
        with tabs[i]:
            df_v = load_data(f"SELECT id, name, brand, model, license_plate, maintenance_notes, control_valid_until, tachograph_valid_until, speed_limiter_valid_until FROM vehicles WHERE type='{t}'")
            if not df_v.empty:
                df_v.columns = ["ID", "Nom", "Marque", "Modèle", "Immat", "Remorqueur/Notes", "Fin CT", "Fin Chrono", "Fin Limiteur"]
                st.dataframe(df_v, use_container_width=True, hide_index=True)
            else:
                st.info(f"Aucun {t.lower()} enregistré.")
                
    st.write("### ✏️ Éditer un véhicule")
    df_all_v = load_data("SELECT id, license_plate, name FROM vehicles")
    if not df_all_v.empty:
        v_dict = dict(zip(df_all_v['id'], df_all_v['license_plate'] + " (" + df_all_v['name'].fillna('') + ")"))
        edit_v_id = st.selectbox("Choisir un véhicule", options=[None] + list(v_dict.keys()), format_func=lambda x: "---" if x is None else v_dict[x])
        if edit_v_id:
            row_v = load_data(f"SELECT * FROM vehicles WHERE id = '{edit_v_id}'").iloc[0]
            with st.form("edit_v"):
                st.write(f"Modification de {row_v['license_plate']}")
                new_ct = st.date_input("Fin CT", value=row_v['control_valid_until'])
                new_chrono = st.date_input("Fin Chrono", value=row_v['tachograph_valid_until'] if pd.notna(row_v['tachograph_valid_until']) else datetime.date.today())
                new_limiteur = st.date_input("Fin Limiteur", value=row_v['speed_limiter_valid_until'] if pd.notna(row_v['speed_limiter_valid_until']) else datetime.date.today())
                if st.form_submit_button("💾 Mettre à jour"):
                    run_query("UPDATE vehicles SET control_valid_until=:ct, tachograph_valid_until=:ch, speed_limiter_valid_until=:li WHERE id=:id",
                              {"ct": new_ct, "ch": new_chrono, "li": new_limiteur, "id": edit_v_id})
                    st.success("Mis à jour !")
                    st.rerun()
"""

# Replace completely the check_alerts function
new_alerts_code = """# --- VERIFICATION DES ALERTES (CHAUFFEURS & VEHICULES) ---
def check_alerts():
    alerts = []
    today = datetime.date.today()
    warning_driver = today + datetime.timedelta(days=60) # 2 mois avant
    warning_driver_after = today - datetime.timedelta(days=30) # 1 mois après (on garde l'alerte même dépassée)
    
    df_d = load_data("SELECT first_name, last_name, license_expiry, caces_expiry, fimo_fco_expiry, driver_card_expiry FROM drivers WHERE is_active = true")
    if not df_d.empty:
        for _, row in df_d.iterrows():
            nom = f"{row['first_name']} {row['last_name']}"
            
            # Vérification Permis (Entre -1 mois et +2 mois)
            if pd.notna(row['license_expiry']):
                if today > row['license_expiry']:
                    alerts.append(f"🚨 **Permis expiré** pour {nom} depuis le {row['license_expiry'].strftime('%d/%m/%Y')} !")
                elif row['license_expiry'] <= warning_driver:
                    alerts.append(f"⚠️ **Permis** de {nom} expire bientôt le {row['license_expiry'].strftime('%d/%m/%Y')} !")
                    
            # Vérification FCO
            if pd.notna(row['fimo_fco_expiry']):
                if today > row['fimo_fco_expiry']:
                    alerts.append(f"🚨 **FCO expirée** pour {nom} depuis le {row['fimo_fco_expiry'].strftime('%d/%m/%Y')} !")
                elif row['fimo_fco_expiry'] <= warning_driver:
                    alerts.append(f"⚠️ **FCO** de {nom} expire le {row['fimo_fco_expiry'].strftime('%d/%m/%Y')} !")
                    
            # Vérification Carte Conducteur
            if pd.notna(row['driver_card_expiry']):
                if today > row['driver_card_expiry']:
                    alerts.append(f"🚨 **Carte Conducteur expirée** pour {nom} depuis le {row['driver_card_expiry'].strftime('%d/%m/%Y')} !")
                elif row['driver_card_expiry'] <= warning_driver:
                    alerts.append(f"⚠️ **Carte Conducteur** de {nom} expire le {row['driver_card_expiry'].strftime('%d/%m/%Y')} !")

    warning_veh = today + datetime.timedelta(days=30) # 1 mois avant
    df_v = load_data("SELECT license_plate, type, control_valid_until, tachograph_valid_until, speed_limiter_valid_until FROM vehicles WHERE is_available = true")
    if not df_v.empty:
        for _, row in df_v.iterrows():
            plaque = row['license_plate']
            if pd.notna(row['control_valid_until']) and row['control_valid_until'] <= warning_veh:
                alerts.append(f"🚚 **CT** du {plaque} expire le {row['control_valid_until'].strftime('%d/%m/%Y')} !")
            if pd.notna(row['tachograph_valid_until']) and row['tachograph_valid_until'] <= warning_veh:
                alerts.append(f"🚚 **Chronotachygraphe** du {plaque} expire le {row['tachograph_valid_until'].strftime('%d/%m/%Y')} !")
            if pd.notna(row['speed_limiter_valid_until']) and row['speed_limiter_valid_until'] <= warning_veh:
                alerts.append(f"🚚 **Limiteur** du {plaque} expire le {row['speed_limiter_valid_until'].strftime('%d/%m/%Y')} !")

    return alerts
"""

# 1. Update check_alerts
content = re.sub(r'# --- VERIFICATION DES ALERTES.*?return alerts\n', new_alerts_code, content, flags=re.DOTALL)

# 2. Re-inject pages before "Vue Chauffeur"
if 'elif navigation == "📱 Vue Chauffeur (Mobile)":' in content:
    # First, let's remove any empty elif blocks we might have left
    content = content.replace('elif navigation == "👥 Chauffeurs":', '')
    content = content.replace('elif navigation == "🚚 Flotte":', '')
    
    content = content.replace('elif navigation == "📱 Vue Chauffeur (Mobile)":', chauffeurs_code + '\nelif navigation == "📱 Vue Chauffeur (Mobile)":')
    with open("app.py", "w") as f:
        f.write(content)
    print("Injected successfully!")
else:
    print("Could not find anchor for injection.")

