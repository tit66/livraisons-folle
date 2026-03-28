import re

with open("app.py", "r") as f:
    content = f.read()

old_block = """            st.write("### 🚚 Véhicule du jour")
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
            
            st.divider()"""

new_block = """            st.write("### 🚚 Mes Véhicules")
            st.caption("Cliquez sur l'immatriculation pour signaler un problème (usure, casse, saleté...).")
            
            df_all_veh = load_data("SELECT id, license_plate, name, type FROM vehicles WHERE is_available = true")
            veh_dict = dict(zip(df_all_veh['id'], df_all_veh['license_plate'] + " - " + df_all_veh['type'] + " (" + df_all_veh['name'].fillna('') + ")"))
            keys_list = [None] + list(veh_dict.keys())

            def issue_form(veh_id, form_key):
                with st.form(form_key):
                    if veh_id is None:
                        veh_id = st.selectbox("Véhicule concerné :", options=keys_list, format_func=lambda x: "--- Choisir un véhicule ---" if x is None else veh_dict[x])
                    
                    issue_type = st.selectbox("Type de problème", ["Pneu usé / crevé", "Feu cassé", "Carrosserie endommagée", "Intérieur sale", "Problème moteur / Voyant", "Autre"])
                    desc = st.text_area("Explication détaillée du problème", placeholder="Ex: Feu arrière droit brisé en reculant ce matin...")
                    
                    import base64
                    photo_file = st.file_uploader("Prendre / Joindre une photo 📸", type=["jpg", "jpeg", "png"])
                    
                    submitted = st.form_submit_button("Envoyer le signalement 🚀", type="primary")
                    if submitted:
                        if veh_id and desc:
                            photo_b64 = ""
                            if photo_file is not None:
                                photo_b64 = base64.b64encode(photo_file.read()).decode()
                                
                            run_query(
                                "INSERT INTO vehicle_issues (driver_id, vehicle_id, description, photo_data) VALUES (:did, :vid, :desc, :pic)",
                                {"did": chauffeur_id, "vid": veh_id, "desc": f"[{issue_type}] {desc}", "pic": photo_b64}
                            )
                            st.success("✅ Problème signalé !")
                            st.rerun()
                        else:
                            st.error("⚠️ L'explication et le véhicule sont obligatoires.")

            if assigned_truck_id:
                with st.expander(f"🚛 Camion assigné : {assigned_truck_label}"):
                    issue_form(assigned_truck_id, "form_truck")
                if assigned_trailer_label:
                    with st.expander(f"🔗 Remorque assignée : {assigned_trailer_label}"):
                        issue_form(assigned_trailer_label_id, "form_trailer")  # Wait, I don't have trailer ID cleanly assigned here... I'll fix this in python.
            else:
                st.warning("Aucun véhicule assigné automatiquement aujourd'hui.")
                
            with st.expander("🚨 Signaler un problème sur un AUTRE véhicule"):
                issue_form(None, "form_other")
                
            st.divider()"""

# Note: The trailer ID needs to be captured properly.
new_block_fixed = """            st.write("### 🚚 Mes Véhicules")
            st.caption("Cliquez sur l'immatriculation pour afficher le formulaire de signalement.")
            
            df_all_veh = load_data("SELECT id, license_plate, name, type FROM vehicles WHERE is_available = true")
            veh_dict = dict(zip(df_all_veh['id'], df_all_veh['license_plate'] + " - " + df_all_veh['type'] + " (" + df_all_veh['name'].fillna('') + ")"))
            keys_list = [None] + list(veh_dict.keys())

            def issue_form(veh_id, form_key):
                with st.form(form_key):
                    final_veh_id = veh_id
                    if veh_id is None:
                        final_veh_id = st.selectbox("Véhicule concerné :", options=keys_list, format_func=lambda x: "--- Choisir un véhicule ---" if x is None else veh_dict[x])
                    
                    issue_type = st.selectbox("Type de problème", ["Pneu usé / crevé", "Feu cassé", "Carrosserie endommagée", "Intérieur sale", "Problème moteur / Voyant", "Autre"])
                    desc = st.text_area("Explication détaillée du problème", placeholder="Ex: Feu arrière droit brisé en reculant ce matin...")
                    
                    import base64
                    photo_file = st.file_uploader("Prendre / Joindre une photo 📸", type=["jpg", "jpeg", "png"])
                    
                    submitted = st.form_submit_button("Envoyer le signalement 🚀", type="primary", use_container_width=True)
                    if submitted:
                        if final_veh_id and desc:
                            photo_b64 = ""
                            if photo_file is not None:
                                photo_b64 = base64.b64encode(photo_file.read()).decode()
                                
                            run_query(
                                "INSERT INTO vehicle_issues (driver_id, vehicle_id, description, photo_data) VALUES (:did, :vid, :desc, :pic)",
                                {"did": chauffeur_id, "vid": final_veh_id, "desc": f"[{issue_type}] {desc}", "pic": photo_b64}
                            )
                            st.success("✅ Problème signalé et transmis au bureau !")
                        else:
                            st.error("⚠️ L'explication détaillée est obligatoire.")

            assigned_trailer_id = None
            if not df_assigned.empty and pd.notna(df_assigned.iloc[0]['t_id']):
                assigned_trailer_id = df_assigned.iloc[0]['t_id']

            if assigned_truck_id:
                with st.expander(f"🚛 Camion : {assigned_truck_label}"):
                    issue_form(assigned_truck_id, "form_truck")
                if assigned_trailer_label:
                    with st.expander(f"🔗 Remorque : {assigned_trailer_label}"):
                        issue_form(assigned_trailer_id, "form_trailer")
            else:
                st.warning("Aucun véhicule assigné automatiquement aujourd'hui.")
                
            with st.expander("🚨 Signaler un problème sur un AUTRE véhicule"):
                issue_form(None, "form_other")
                
            st.divider()"""

if old_block in content:
    content = content.replace(old_block, new_block_fixed)
    with open("app.py", "w") as f:
        f.write(content)
    print("Mobile UI updated!")
else:
    print("Could not find mobile block.")

