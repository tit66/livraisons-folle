import re

with open("app.py", "r") as f:
    content = f.read()

old_client_block = """    if not df_clients.empty:
        client_dict = dict(zip(df_clients['id'], df_clients['name']))
        selected_client_id = st.selectbox("1️⃣ Client", options=[None] + list(client_dict.keys()), format_func=lambda x: "--- Choisir un client ---" if x is None else client_dict[x])
        
        if selected_client_id:
            df_sites = load_data("SELECT id, label, address, gmaps_link FROM sites WHERE client_id = :cid AND is_active = true", {"cid": selected_client_id})"""

new_client_block = """    client_dict = {"NEW_CLIENT": "➕ NOUVEAU CLIENT PRO OU PARTICULIER"}
    if not df_clients.empty:
        for idx, row in df_clients.iterrows():
            client_dict[row['id']] = row['name']
            
    selected_client_id = st.selectbox("1️⃣ Client", options=[None] + list(client_dict.keys()), format_func=lambda x: "--- Choisir un client ---" if x is None else client_dict[x])
    
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
        
        st.divider()
        prestation = st.radio("3️⃣ Type de Prestation", ["Livraison de matériaux", "Location de benne", "Autre"], horizontal=True)

    elif selected_client_id is not None:
        df_sites = load_data("SELECT id, label, address, gmaps_link FROM sites WHERE client_id = :cid AND is_active = true", {"cid": selected_client_id})"""

if old_client_block in content:
    content = content.replace(old_client_block, new_client_block)
else:
    print("Failed to replace client block")

old_save_block = """            if st.button("✅ Valider et Enregistrer", type="primary", use_container_width=True, disabled=not est_valide):
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

new_save_block = """            if st.button("✅ Valider et Enregistrer", type="primary", use_container_width=True, disabled=not est_valide):
                try:
                    final_client_id = selected_client_id
                    final_site_id = None
                    
                    # 1. GESTION DE LA CREATION DE CLIENT COMPLET
                    if selected_client_id == "NEW_CLIENT":
                        if not new_c_name:
                            st.error("Le Nom du client est obligatoire.")
                            st.stop()
                            
                        # Insertion du client
                        res_c = run_query(\"\"\"
                            INSERT INTO clients (name, type, email, phone, billing_address)
                            VALUES (:n, :t, :e, :p, :a) RETURNING id
                        \"\"\", {"n": new_c_name, "t": new_c_type, "e": new_c_email, "p": new_c_phone, "a": new_c_address}).fetchone()
                        
                        final_client_id = res_c[0]
                        st.success(f"👤 Nouveau client {new_c_name} créé !")
                        
                        # Insertion du site initial pour ce client
                        addr_site = new_s_address if new_s_address else new_c_address
                        lbl_site = new_s_label if new_s_label else "Adresse principale"
                        res_s = run_query(\"\"\"
                            INSERT INTO sites (client_id, label, address, gmaps_link, is_active)
                            VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id
                        \"\"\", {"cid": final_client_id, "lbl": lbl_site, "addr": addr_site, "gmaps": new_s_gmaps}).fetchone()
                        
                        final_site_id = res_s[0]
                        
                    # 2. GESTION DU CLIENT EXISTANT MAIS NOUVEAU CHANTIER
                    elif selected_site_id == "NEW":
                        if not new_site_address:
                            st.error("L'adresse du chantier est obligatoire.")
                            st.stop()
                        lbl = new_site_label if new_site_label else "Nouvelle Adresse"
                        res = run_query(\"\"\"
                            INSERT INTO sites (client_id, label, address, gmaps_link, is_active) 
                            VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id
                        \"\"\", {"cid": final_client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps}).fetchone()
                        final_site_id = res[0]
                        st.success(f"📍 Le nouveau chantier a été sauvegardé dans la fiche du client.")
                    
                    # 3. CLIENT EXISTANT ET CHANTIER EXISTANT
                    else:
                        final_site_id = selected_site_id

                    # 4. ENREGISTREMENT DE LA COMMANDE (Commun à tous les cas)
                    insert_query = \"\"\"
                    INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons, container_type, waste_type, instructions, status, source, requested_date, requested_slot) 
                    VALUES (:client_id, :site_id, :service_type, :material, :quantity, :container_type, :waste_type, :instructions, 'pending', 'admin_streamlit', :req_date, :req_slot)
                    \"\"\"
                    service_final = f"Benne - {action_benne}" if prestation == "Location de benne" else prestation
                    run_query(insert_query, {
                        "client_id": final_client_id, "site_id": final_site_id, "service_type": service_final,
                        "material": marchandise, "quantity": quantite, "container_type": volume_benne,
                        "waste_type": type_benne, "instructions": instructions, "req_date": date_livraison, "req_slot": creneau_choisi
                    })
                    st.success(f"🎉 Commande enregistrée pour le {date_livraison.strftime('%d/%m/%Y')} (Créneau : {creneau_choisi}).")
                    
                except Exception as e:
                    st.error(f"Erreur SQL globale : {e}")"""

if old_save_block in content:
    content = content.replace(old_save_block, new_save_block)
    with open("app.py", "w") as f:
        f.write(content)
    print("Success 2")
else:
    print("Failed to replace save block")

