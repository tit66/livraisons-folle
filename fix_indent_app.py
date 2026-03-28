with open("app.py", "r") as f:
    content = f.read()

# Replace the entire try/except block for the button with perfect indentation
old_block = """            if st.button("✅ Valider et Enregistrer", type="primary", use_container_width=True, disabled=not est_valide):
                try:
                    final_client_id = selected_client_id
                    final_site_id = None
                    
                    if selected_client_id == "NEW_CLIENT":
                        if not new_c_name:
                            st.error("Le Nom du client est obligatoire.")
                            st.stop()
                        res_c = run_query(\"\"\"INSERT INTO clients (name, type, email, phone, billing_address) VALUES (:n, :t, :e, :p, :a) RETURNING id\"\"\", {"n": new_c_name, "t": new_c_type, "e": new_c_email, "p": new_c_phone, "a": new_c_address}).fetchone()
                        final_client_id = res_c[0]
                        st.success(f"👤 Nouveau client {new_c_name} créé !")
                        addr_site = new_s_address if new_s_address else new_c_address
                        lbl_site = new_s_label if new_s_label else "Adresse principale"
                        res_s = run_query(\"\"\"INSERT INTO sites (client_id, label, address, gmaps_link, is_active) VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id\"\"\", {"cid": final_client_id, "lbl": lbl_site, "addr": addr_site, "gmaps": new_s_gmaps}).fetchone()
                        final_site_id = res_s[0]
                        
                    elif selected_site_id == "NEW":
                        if not new_site_address:
                            st.error("L'adresse du chantier est obligatoire.")
                            st.stop()
                        lbl = new_site_label if new_site_label else "Nouvelle Adresse"
                        res = run_query(\"\"\"INSERT INTO sites (client_id, label, address, gmaps_link, is_active) VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id\"\"\", {"cid": final_client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps}).fetchone()
                        if res: final_site_id = res[0]
                        st.success(f"📍 Le nouveau chantier a été sauvegardé dans la fiche du client.")
                    
                    else:
                        final_site_id = selected_site_id
                        
                    insert_query = \"\"\"INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons, container_type, waste_type, instructions, status, source, requested_date, requested_slot) VALUES (:client_id, :site_id, :service_type, :material, :quantity, :container_type, :waste_type, :instructions, 'pending', 'admin_streamlit', :req_date, :req_slot)\"\"\"
                    service_final = f"Benne - {action_benne}" if prestation == "Location de benne" else prestation
                    run_query(insert_query, {"client_id": final_client_id, "site_id": final_site_id, "service_type": service_final, "material": marchandise, "quantity": quantite, "container_type": volume_benne, "waste_type": type_benne, "instructions": instructions, "req_date": date_livraison, "req_slot": creneau_choisi})
                    st.success(f"🎉 Commande enregistrée pour le {date_livraison.strftime('%d/%m/%Y')} (Créneau : {creneau_choisi}).")
                    
                except Exception as e:
                    st.error(f"Erreur SQL globale : {e}")"""

# First find what is actually there
import re
pattern = re.compile(r'            if st\.button\("✅ Valider et Enregistrer".*?                except Exception as e:\n                    st\.error\(f"Erreur SQL globale : \{e\}"\)', re.DOTALL)

new_block = """            if st.button("✅ Valider et Enregistrer", type="primary", use_container_width=True, disabled=not est_valide):
                try:
                    final_client_id = selected_client_id
                    final_site_id = None
                    
                    if selected_client_id == "NEW_CLIENT":
                        if not new_c_name:
                            st.error("Le Nom du client est obligatoire.")
                            st.stop()
                        res_c = run_query("INSERT INTO clients (name, type, email, phone, billing_address) VALUES (:n, :t, :e, :p, :a) RETURNING id", {"n": new_c_name, "t": new_c_type, "e": new_c_email, "p": new_c_phone, "a": new_c_address}).fetchone()
                        final_client_id = res_c[0]
                        st.success(f"👤 Nouveau client {new_c_name} créé !")
                        addr_site = new_s_address if new_s_address else new_c_address
                        lbl_site = new_s_label if new_s_label else "Adresse principale"
                        res_s = run_query("INSERT INTO sites (client_id, label, address, gmaps_link, is_active) VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id", {"cid": final_client_id, "lbl": lbl_site, "addr": addr_site, "gmaps": new_s_gmaps}).fetchone()
                        final_site_id = res_s[0]
                        
                    elif selected_site_id == "NEW":
                        if not new_site_address:
                            st.error("L'adresse du chantier est obligatoire.")
                            st.stop()
                        lbl = new_site_label if new_site_label else "Nouvelle Adresse"
                        res = run_query("INSERT INTO sites (client_id, label, address, gmaps_link, is_active) VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id", {"cid": final_client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps}).fetchone()
                        if res: final_site_id = res[0]
                        st.success(f"📍 Le nouveau chantier a été sauvegardé dans la fiche du client.")
                    
                    else:
                        final_site_id = selected_site_id
                        
                    insert_query = "INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons, container_type, waste_type, instructions, status, source, requested_date, requested_slot) VALUES (:client_id, :site_id, :service_type, :material, :quantity, :container_type, :waste_type, :instructions, 'pending', 'admin_streamlit', :req_date, :req_slot)"
                    service_final = f"Benne - {action_benne}" if prestation == "Location de benne" else prestation
                    run_query(insert_query, {"client_id": final_client_id, "site_id": final_site_id, "service_type": service_final, "material": marchandise, "quantity": quantite, "container_type": volume_benne, "waste_type": type_benne, "instructions": instructions, "req_date": date_livraison, "req_slot": creneau_choisi})
                    st.success(f"🎉 Commande enregistrée pour le {date_livraison.strftime('%d/%m/%Y')} (Créneau : {creneau_choisi}).")
                    
                except Exception as e:
                    st.error(f"Erreur SQL globale : {e}")"""

if pattern.search(content):
    content = pattern.sub(new_block, content)
    with open("app.py", "w") as f:
        f.write(content)
    print("Success regex")
else:
    print("Failed regex")

