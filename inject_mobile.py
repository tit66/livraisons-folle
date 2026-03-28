import re

with open("app.py", "r") as f:
    content = f.read()

old_mobile_block = """elif navigation == "📱 Vue Chauffeur (Mobile)":
    st.title("📱 Interface Chauffeur")
    st.write("Vue simplifiée sur smartphone pour les missions du jour.")
    
    chauffeur_connecte = st.selectbox("Se connecter en tant que :", ["Marcel", "Jean", "Paul"])
    st.success(f"👋 Bonjour {chauffeur_connecte} ! Voici tes missions pour aujourd'hui :")
    
    with st.expander("Mission 1 : 08h00 - Livraison Sable", expanded=True):
        st.write("**Client :** Entreprise Martin")
        st.write("**Adresse :** 12 rue de la Paix, Perpignan")
        st.write("**Détails :** 15 Tonnes de Sable")
        st.write("**Instructions :** Code portail 1234")
        st.button("✅ Marquer comme LIVRÉ", key="btn1")
        
    with st.expander("Mission 2 : 10h30 - Rotation Benne", expanded=True):
        st.write("**Client :** Particulier Dupont")
        st.write("**Adresse :** 45 avenue des Fleurs, Cabestany")
        st.write("**Détails :** Rotation Benne 10m3 Gravats")
        st.write("**Instructions :** Attention, petite cour, manœuvrer avec précaution.")
        st.button("✅ Marquer comme TERMINÉ", key="btn2")"""

new_mobile_block = """elif navigation == "📱 Vue Chauffeur (Mobile)":
    st.title("📱 Interface Chauffeur")
    st.write("Vue simplifiée sur smartphone pour les missions du jour.")
    
    df_drivers = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true")
    if not df_drivers.empty:
        driver_dict = dict(zip(df_drivers['id'], df_drivers['first_name'] + " " + df_drivers['last_name']))
        chauffeur_id = st.selectbox("Se connecter en tant que :", options=[None] + list(driver_dict.keys()), format_func=lambda x: "--- Sélectionner ---" if x is None else driver_dict[x])
        
        if chauffeur_id:
            chauffeur_nom = driver_dict[chauffeur_id]
            st.success(f"👋 Bonjour {chauffeur_nom} !")
            
            today_str = datetime.date.today().strftime('%Y-%m-%d')
            df_assigned = load_data(f\"\"\"
                SELECT v.id as v_id, v.license_plate as v_plate, v.name as v_name,
                       t.id as t_id, t.license_plate as t_plate, t.name as t_name
                FROM orders o
                JOIN vehicles v ON o.vehicle_id = v.id
                LEFT JOIN vehicles t ON o.trailer_id = t.id
                WHERE o.driver_id = {chauffeur_id} AND o.requested_date = '{today_str}'
                LIMIT 1
            \"\"\")
            
            assigned_truck_id = None
            assigned_truck_label = ""
            assigned_trailer_label = ""
            
            if not df_assigned.empty:
                assigned_truck_id = df_assigned.iloc[0]['v_id']
                assigned_truck_label = f"{df_assigned.iloc[0]['v_plate']} ({df_assigned.iloc[0]['v_name']})"
                if pd.notna(df_assigned.iloc[0]['t_id']):
                    assigned_trailer_label = f"{df_assigned.iloc[0]['t_plate']} ({df_assigned.iloc[0]['t_name']})"
                    
            st.write("### 🚚 Véhicule du jour")
            if assigned_truck_id:
                col1, col2 = st.columns(2)
                col1.metric("Camion assigné", assigned_truck_label)
                if assigned_trailer_label:
                    col2.metric("Remorque assignée", assigned_trailer_label)
                else:
                    col2.metric("Remorque assignée", "Aucune")
            else:
                st.warning("Aucun véhicule assigné automatiquement aujourd'hui dans le planning.")
                
            st.divider()
            st.write("### 🚨 Signaler un problème véhicule")
            df_all_veh = load_data("SELECT id, license_plate, name, type FROM vehicles WHERE is_available = true")
            veh_dict = dict(zip(df_all_veh['id'], df_all_veh['license_plate'] + " - " + df_all_veh['type'] + " (" + df_all_veh['name'].fillna('') + ")"))
            
            # Default to assigned truck if available
            default_veh_index = 0
            keys_list = [None] + list(veh_dict.keys())
            if assigned_truck_id and assigned_truck_id in keys_list:
                default_veh_index = keys_list.index(assigned_truck_id)
                
            vehicule_prob_id = st.selectbox("Véhicule concerné :", options=keys_list, index=default_veh_index, format_func=lambda x: "--- Choisir un véhicule ---" if x is None else veh_dict[x])
            
            with st.form("issue_report_form"):
                issue_type = st.selectbox("Type de problème", ["Pneu usé / crevé", "Feu cassé", "Carrosserie endommagée", "Intérieur sale", "Problème moteur / Voyant", "Autre"])
                desc = st.text_area("Explication détaillée du problème", placeholder="Ex: Feu arrière droit brisé en reculant ce matin...")
                
                import base64
                photo_file = st.file_uploader("Prendre / Joindre une photo 📸", type=["jpg", "jpeg", "png"])
                
                submitted = st.form_submit_button("Envoyer le signalement 🚀", type="primary")
                if submitted:
                    if vehicule_prob_id and desc:
                        photo_b64 = ""
                        if photo_file is not None:
                            photo_b64 = base64.b64encode(photo_file.read()).decode()
                            
                        run_query(
                            "INSERT INTO vehicle_issues (driver_id, vehicle_id, description, photo_data) VALUES (:did, :vid, :desc, :pic)",
                            {"did": chauffeur_id, "vid": vehicule_prob_id, "desc": f"[{issue_type}] {desc}", "pic": photo_b64}
                        )
                        st.success("✅ Problème signalé et transmis au bureau !")
                    else:
                        st.error("⚠️ Veuillez sélectionner le véhicule et fournir une explication.")
            
            st.divider()
            st.write("### 📋 Mes missions du jour")
            df_missions = load_data(f"SELECT o.id, c.name, o.dropoff_address, o.service_type, o.material, o.quantity_tons, o.instructions, o.status FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.driver_id = {chauffeur_id} AND o.requested_date = '{today_str}' ORDER BY o.created_at")
            
            if not df_missions.empty:
                for idx, m in df_missions.iterrows():
                    with st.expander(f"Mission {idx+1} : {m['service_type']} - {m['status']}", expanded=(m['status']!='done')):
                        st.write(f"**Client :** {m['name'] if pd.notna(m['name']) else 'Non spécifié'}")
                        st.write(f"**Adresse :** {m['dropoff_address'] if pd.notna(m['dropoff_address']) else 'Non spécifiée'}")
                        st.write(f"**Détails :** {m['quantity_tons'] if pd.notna(m['quantity_tons']) else '?'} T de {m['material'] if pd.notna(m['material']) else 'Non spécifié'}")
                        if pd.notna(m['instructions']) and m['instructions'].strip() != "":
                            st.write(f"**Instructions :** {m['instructions']}")
                        
                        if m['status'] != 'done':
                            if st.button("✅ Marquer comme TERMINÉ", key=f"btn_done_{m['id']}"):
                                run_query("UPDATE orders SET status='done' WHERE id=:oid", {"oid": m['id']})
                                st.rerun()
                        else:
                            st.success("Mission terminée !")
            else:
                st.info("Aucune mission assignée aujourd'hui.")
    else:
        st.info("Veuillez d'abord créer des chauffeurs dans la gestion des Chauffeurs.")"""

if old_mobile_block in content:
    content = content.replace(old_mobile_block, new_mobile_block)
    with open("app.py", "w") as f:
        f.write(content)
    print("Mobile module successfully updated.")
else:
    print("Failed to replace mobile block.")
