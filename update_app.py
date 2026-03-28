import re

with open("app.py", "r") as f:
    content = f.read()

# On va remplacer la fin de l'onglet Chauffeurs pour rajouter l'édition
old_block = """        df_d = load_data("SELECT first_name as \\"Prénom\\", last_name as \\"Nom\\", phone as \\"Téléphone\\", license_expiry as \\"Fin Permis\\", fimo_fco_expiry as \\"Fin FIMO/FCO\\", driver_card_expiry as \\"Fin Carte Conducteur\\" FROM drivers")
        if not df_d.empty:
            df_d['Fin Permis'] = pd.to_datetime(df_d['Fin Permis']).dt.strftime('%d/%m/%Y')
            df_d['Fin FIMO/FCO'] = pd.to_datetime(df_d['Fin FIMO/FCO']).dt.strftime('%d/%m/%Y')
            df_d['Fin Carte Conducteur'] = pd.to_datetime(df_d['Fin Carte Conducteur']).dt.strftime('%d/%m/%Y')
            st.dataframe(df_d, use_container_width=True, hide_index=True)"""

new_block = """        st.subheader("📋 Liste & Modification des chauffeurs")
        df_d_full = load_data("SELECT * FROM drivers ORDER BY first_name")
        
        if not df_d_full.empty:
            # Affichage simplifié
            df_display = df_d_full[['id', 'first_name', 'last_name', 'phone', 'license_expiry', 'fimo_fco_expiry', 'driver_card_expiry', 'is_active']].copy()
            df_display.columns = ["ID", "Prénom", "Nom", "Téléphone", "Fin Permis", "Fin FIMO/FCO", "Fin Carte Cond.", "Actif"]
            for col in ["Fin Permis", "Fin FIMO/FCO", "Fin Carte Cond."]:
                df_display[col] = pd.to_datetime(df_display[col]).dt.strftime('%d/%m/%Y')
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.divider()
            st.write("### ✏️ Modifier un chauffeur existant")
            driver_dict = dict(zip(df_d_full['id'], df_d_full['first_name'] + " " + df_d_full['last_name']))
            selected_edit_id = st.selectbox("Choisir le chauffeur à modifier", options=[None] + list(driver_dict.keys()), format_func=lambda x: "--- Sélectionner ---" if x is None else driver_dict[x])
            
            if selected_edit_id:
                driver_data = df_d_full[df_d_full['id'] == selected_edit_id].iloc[0]
                
                with st.form("edit_driver_form"):
                    st.write(f"Modification du profil de **{driver_data['first_name']} {driver_data['last_name']}**")
                    c_e1, c_e2 = st.columns(2)
                    
                    with c_e1:
                        new_phone = st.text_input("Téléphone", value=driver_data['phone'] if pd.notna(driver_data['phone']) else "")
                        new_email = st.text_input("Email", value=driver_data['email'] if pd.notna(driver_data['email']) else "")
                        is_active = st.checkbox("Chauffeur Actif (Décocher s'il a quitté l'entreprise)", value=bool(driver_data['is_active']))
                        
                    with c_e2:
                        new_permis = st.date_input("Fin validité Permis", pd.to_datetime(driver_data['license_expiry']).date() if pd.notna(driver_data['license_expiry']) else datetime.date.today(), format="DD/MM/YYYY")
                        new_fimo = st.date_input("Fin validité FIMO/FCO", pd.to_datetime(driver_data['fimo_fco_expiry']).date() if pd.notna(driver_data['fimo_fco_expiry']) else datetime.date.today(), format="DD/MM/YYYY")
                        new_carte = st.date_input("Fin validité Carte Conducteur", pd.to_datetime(driver_data['driver_card_expiry']).date() if pd.notna(driver_data['driver_card_expiry']) else datetime.date.today(), format="DD/MM/YYYY")
                        new_caces = st.date_input("Fin validité CACES", pd.to_datetime(driver_data['caces_expiry']).date() if pd.notna(driver_data['caces_expiry']) else datetime.date.today(), format="DD/MM/YYYY")

                    if st.form_submit_button("💾 Mettre à jour", type="primary"):
                        run_query(\"\"\"
                            UPDATE drivers 
                            SET phone = :ph, email = :em, is_active = :act, 
                                license_expiry = :lp, fimo_fco_expiry = :fimo, driver_card_expiry = :carte, caces_expiry = :cac
                            WHERE id = :id
                        \"\"\", {
                            "ph": new_phone, "em": new_email, "act": is_active,
                            "lp": new_permis, "fimo": new_fimo, "carte": new_carte, "cac": new_caces, "id": selected_edit_id
                        })
                        st.success("✅ Profil mis à jour !")
                        st.rerun()
        else:
            st.info("Aucun chauffeur dans la base.")"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("app.py", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Failed to find block")

