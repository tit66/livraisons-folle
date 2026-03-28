import re

with open("app.py", "r") as f:
    content = f.read()

old_cmd_block = """            df_sites = load_data("SELECT id, label, address FROM sites WHERE client_id = :cid AND is_active = true", {"cid": selected_client_id})
            site_options = {None: "--- Aucun chantier spécifique ---"}
            if not df_sites.empty:
                for _, row in df_sites.iterrows(): site_options[row['id']] = f"{row['label']} - {row['address']}"
            selected_site_id = st.selectbox("2️⃣ Chantier", options=list(site_options.keys()), format_func=lambda x: site_options[x])
            
            st.divider()
            prestation = st.radio("3️⃣ Type de Prestation", ["Livraison de matériaux", "Location de benne", "Autre"], horizontal=True)"""

new_cmd_block = """            df_sites = load_data("SELECT id, label, address, gmaps_link FROM sites WHERE client_id = :cid AND is_active = true", {"cid": selected_client_id})
            
            site_options = {"NEW": "➕ Créer une nouvelle adresse/chantier", None: "--- Adresse de facturation du client ---"}
            if not df_sites.empty:
                for _, row in df_sites.iterrows(): 
                    site_options[row['id']] = f"📍 {row['label']} - {row['address']}"
                    
            selected_site_id = st.selectbox("2️⃣ Chantier / Adresse de livraison", options=list(site_options.keys()), format_func=lambda x: site_options[x])
            
            # Variables for new site
            new_site_label, new_site_address, new_site_gmaps = None, None, None
            
            if selected_site_id == "NEW":
                st.info("Saisissez les informations de la nouvelle adresse de livraison. Elle sera sauvegardée pour ce client.")
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    new_site_label = st.text_input("Nom du chantier (Ex: Construction Villa Dupont)")
                    new_site_address = st.text_area("Adresse exacte *")
                with c_s2:
                    new_site_gmaps = st.text_input("Lien Google Maps (Points GPS, Optionnel mais recommandé pour les chauffeurs)")
                    st.caption("Allez sur Google Maps, placez un repère, cliquez sur 'Partager' puis 'Copier le lien'.")
            elif selected_site_id is not None:
                # Display info of selected site
                site_info = df_sites[df_sites['id'] == selected_site_id].iloc[0]
                if pd.notna(site_info['gmaps_link']) and site_info['gmaps_link'].strip() != "":
                    st.markdown(f"*(Lien GPS enregistré pour ce chantier : [Ouvrir Maps]({site_info['gmaps_link']}))*")
                else:
                    st.markdown("*(Aucun lien GPS spécifique enregistré pour ce chantier)*")
            
            st.divider()
            prestation = st.radio("3️⃣ Type de Prestation", ["Livraison de matériaux", "Location de benne", "Autre"], horizontal=True)"""

if old_cmd_block in content:
    content = content.replace(old_cmd_block, new_cmd_block)
else:
    print("Could not find block 1")

old_save_block = """            if st.button("✅ Valider et Enregistrer", type="primary", use_container_width=True, disabled=not est_valide):
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
                    st.error(f"Erreur : {e}")"""

new_save_block = """            if st.button("✅ Valider et Enregistrer", type="primary", use_container_width=True, disabled=not est_valide):
                if selected_site_id == "NEW" and not new_site_address:
                    st.error("⚠️ Veuillez saisir au moins l'adresse exacte pour le nouveau chantier.")
                else:
                    try:
                        final_site_id = selected_site_id
                        
                        # Si c'est un nouveau chantier, on le crée d'abord dans la base
                        if selected_site_id == "NEW":
                            lbl = new_site_label if new_site_label else "Nouvelle Adresse"
                            res = run_query(\"\"\"
                                INSERT INTO sites (client_id, label, address, gmaps_link, is_active) 
                                VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id
                            \"\"\", {"cid": selected_client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps}).fetchone()
                            if res:
                                final_site_id = res[0]
                        
                        insert_query = \"\"\"
                        INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons, container_type, waste_type, instructions, status, source, requested_date, requested_slot) 
                        VALUES (:client_id, :site_id, :service_type, :material, :quantity, :container_type, :waste_type, :instructions, 'pending', 'admin_streamlit', :req_date, :req_slot)
                        \"\"\"
                        service_final = f"Benne - {action_benne}" if prestation == "Location de benne" else prestation
                        run_query(insert_query, {
                            "client_id": selected_client_id, "site_id": final_site_id, "service_type": service_final,
                            "material": marchandise, "quantity": quantite, "container_type": volume_benne,
                            "waste_type": type_benne, "instructions": instructions, "req_date": date_livraison, "req_slot": creneau_choisi
                        })
                        st.success(f"🎉 Commande enregistrée pour le {date_livraison.strftime('%d/%m/%Y')} (Créneau : {creneau_choisi}).")
                        
                        # Note: pour afficher l'alerte à l'écran sans bloquer
                        if selected_site_id == "NEW":
                            st.success(f"📍 Le nouveau chantier '{new_site_label or 'Nouvelle Adresse'}' a été sauvegardé dans la fiche du client pour les prochaines fois.")
                            
                    except Exception as e:
                        st.error(f"Erreur : {e}")"""

if old_save_block in content:
    content = content.replace(old_save_block, new_save_block)
    with open("app.py", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Could not find block 2")

