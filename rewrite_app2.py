with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.startswith('            if st.button("✅ Valider et Enregistrer"'):
        skip = True
        new_lines.append(line)
        new_lines.append('                try:\n')
        new_lines.append('                    final_client_id = selected_client_id\n')
        new_lines.append('                    final_site_id = None\n')
        new_lines.append('                    \n')
        new_lines.append('                    if selected_client_id == "NEW_CLIENT":\n')
        new_lines.append('                        if not new_c_name:\n')
        new_lines.append('                            st.error("Le Nom du client est obligatoire.")\n')
        new_lines.append('                            st.stop()\n')
        new_lines.append('                        res_c = run_query("""INSERT INTO clients (name, type, email, phone, billing_address) VALUES (:n, :t, :e, :p, :a) RETURNING id""", {"n": new_c_name, "t": new_c_type, "e": new_c_email, "p": new_c_phone, "a": new_c_address}).fetchone()\n')
        new_lines.append('                        final_client_id = res_c[0]\n')
        new_lines.append('                        st.success(f"👤 Nouveau client {new_c_name} créé !")\n')
        new_lines.append('                        addr_site = new_s_address if new_s_address else new_c_address\n')
        new_lines.append('                        lbl_site = new_s_label if new_s_label else "Adresse principale"\n')
        new_lines.append('                        res_s = run_query("""INSERT INTO sites (client_id, label, address, gmaps_link, is_active) VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id""", {"cid": final_client_id, "lbl": lbl_site, "addr": addr_site, "gmaps": new_s_gmaps}).fetchone()\n')
        new_lines.append('                        final_site_id = res_s[0]\n')
        new_lines.append('                        \n')
        new_lines.append('                    elif selected_site_id == "NEW":\n')
        new_lines.append('                        if not new_site_address:\n')
        new_lines.append('                            st.error("L\'adresse du chantier est obligatoire.")\n')
        new_lines.append('                            st.stop()\n')
        new_lines.append('                        lbl = new_site_label if new_site_label else "Nouvelle Adresse"\n')
        new_lines.append('                        res = run_query("""INSERT INTO sites (client_id, label, address, gmaps_link, is_active) VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id""", {"cid": final_client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps}).fetchone()\n')
        new_lines.append('                        if res: final_site_id = res[0]\n')
        new_lines.append('                        st.success(f"📍 Le nouveau chantier a été sauvegardé dans la fiche du client.")\n')
        new_lines.append('                    \n')
        new_lines.append('                    else:\n')
        new_lines.append('                        final_site_id = selected_site_id\n')
        new_lines.append('                        \n')
        new_lines.append('                    insert_query = """INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons, container_type, waste_type, instructions, status, source, requested_date, requested_slot) VALUES (:client_id, :site_id, :service_type, :material, :quantity, :container_type, :waste_type, :instructions, \'pending\', \'admin_streamlit\', :req_date, :req_slot)"""\n')
        new_lines.append('                    service_final = f"Benne - {action_benne}" if prestation == "Location de benne" else prestation\n')
        new_lines.append('                    run_query(insert_query, {"client_id": final_client_id, "site_id": final_site_id, "service_type": service_final, "material": marchandise, "quantity": quantite, "container_type": volume_benne, "waste_type": type_benne, "instructions": instructions, "req_date": date_livraison, "req_slot": creneau_choisi})\n')
        new_lines.append('                    st.success(f"🎉 Commande enregistrée pour le {date_livraison.strftime(\'%d/%m/%Y\')} (Créneau : {creneau_choisi}).")\n')
        new_lines.append('                    \n')
        new_lines.append('                except Exception as e:\n')
        new_lines.append('                    st.error(f"Erreur SQL globale : {e}")\n')
        continue
    
    if skip:
        if line.startswith('    else:'): # Fin de la partie Prise de Commande, on recommence à copier
            skip = False
            new_lines.append(line)
        continue
        
    if not skip:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)
print("Block completely replaced.")
