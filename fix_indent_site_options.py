with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('            site_options = {"NEW": "➕ Créer une nouvelle adresse/chantier"'):
        new_lines.append(line.replace('            site_options', '        site_options'))
    elif line.startswith('            if not df_sites.empty:'):
        new_lines.append(line.replace('            if not', '        if not'))
    elif line.startswith('                for _, row in df_sites.iterrows():'):
        new_lines.append(line.replace('                for', '            for'))
    elif line.startswith('                    site_options[row[\'id\']] = f"📍 {row[\'label\']} - {row[\'address\']}"'):
        new_lines.append(line.replace('                    site_options', '                site_options'))
    elif line.startswith('            selected_site_id = st.selectbox("2️⃣ Chantier / Adresse de livraison"'):
        new_lines.append(line.replace('            selected_site_id', '        selected_site_id'))
    elif line.startswith('            # Variables for new site'):
        new_lines.append(line.replace('            # Variables', '        # Variables'))
    elif line.startswith('            new_site_label, new_site_address, new_site_gmaps = None, None, None'):
        new_lines.append(line.replace('            new_site_label', '        new_site_label'))
    elif line.startswith('            if selected_site_id == "NEW":'):
        new_lines.append(line.replace('            if selected_site_id', '        if selected_site_id'))
    elif line.startswith('                st.info("Saisissez les informations de la nouvelle adresse de livraison'):
        new_lines.append(line.replace('                st.info', '            st.info'))
    elif line.startswith('                c_s1, c_s2 = st.columns(2)'):
        new_lines.append(line.replace('                c_s1', '            c_s1'))
    elif line.startswith('                with c_s1:'):
        new_lines.append(line.replace('                with', '            with'))
    elif line.startswith('                    new_site_label = st.text_input("Nom du chantier'):
        new_lines.append(line.replace('                    new_site_label', '                new_site_label'))
    elif line.startswith('                    new_site_address = st.text_area("Adresse exacte *"'):
        new_lines.append(line.replace('                    new_site_address', '                new_site_address'))
    elif line.startswith('                with c_s2:'):
        new_lines.append(line.replace('                with', '            with'))
    elif line.startswith('                    new_site_gmaps = st.text_input("Lien Google Maps'):
        new_lines.append(line.replace('                    new_site_gmaps', '                new_site_gmaps'))
    elif line.startswith('                    st.caption("Allez sur Google Maps'):
        new_lines.append(line.replace('                    st.caption', '                st.caption'))
    elif line.startswith('            elif selected_site_id is not None:'):
        new_lines.append(line.replace('            elif', '        elif'))
    elif line.startswith('                # Display info of selected site'):
        new_lines.append(line.replace('                #', '            #'))
    elif line.startswith('                site_info = df_sites[df_sites[\'id\'] == selected_site_id].iloc[0]'):
        new_lines.append(line.replace('                site_info', '            site_info'))
    elif line.startswith('                if pd.notna(site_info[\'gmaps_link\']) and site_info[\'gmaps_link\'].strip() != "":'):
        new_lines.append(line.replace('                if pd', '            if pd'))
    elif line.startswith('                    st.markdown(f"*(Lien GPS enregistré pour ce chantier'):
        new_lines.append(line.replace('                    st.markdown', '                st.markdown'))
    elif line.startswith('                else:'):
        new_lines.append(line.replace('                else', '            else'))
    elif line.startswith('                    st.markdown("*(Aucun lien GPS spécifique'):
        new_lines.append(line.replace('                    st.markdown', '                st.markdown'))
    elif line.startswith('            st.divider()'):
        new_lines.append(line.replace('            st.divider', '        st.divider'))
    elif line.startswith('            prestation = st.radio("3️⃣ Type de Prestation"'):
        new_lines.append(line.replace('            prestation', '        prestation'))
    elif line.startswith('            st.write("")'):
        new_lines.append(line.replace('            st.write', '        st.write'))
    elif line.startswith('            colA, colB = st.columns(2)'):
        new_lines.append(line.replace('            colA', '        colA'))
    elif line.startswith('            with colA:'):
        new_lines.append(line.replace('            with', '        with'))
    elif line.startswith('                marchandise, quantite, type_benne, volume_benne, action_benne = None, None, None, None, None'):
        new_lines.append(line.replace('                marchandise', '            marchandise'))
    elif line.startswith('                if prestation == "Livraison de matériaux":'):
        new_lines.append(line.replace('                if prestation', '            if prestation'))
    elif line.startswith('                    marchandise = st.selectbox("Type de marchandise"'):
        new_lines.append(line.replace('                    marchandise', '                marchandise'))
    elif line.startswith('                    quantite = st.number_input("Quantité'):
        new_lines.append(line.replace('                    quantite', '                quantite'))
    elif line.startswith('                elif prestation == "Location de benne":'):
        new_lines.append(line.replace('                elif', '            elif'))
    elif line.startswith('                    action_benne = st.radio("Type d\'intervention"'):
        new_lines.append(line.replace('                    action_benne', '                action_benne'))
    elif line.startswith('                    type_benne = st.selectbox("Type de déchets"'):
        new_lines.append(line.replace('                    type_benne', '                type_benne'))
    elif line.startswith('                    options_volume = ["8m3", "10m3"] if type_benne == "Gravats" else ["8m3", "10m3", "15m3", "30m3"]'):
        new_lines.append(line.replace('                    options_volume', '                options_volume'))
    elif line.startswith('                    if type_benne == "Gravats": st.caption("⚠️'):
        new_lines.append(line.replace('                    if type_benne', '                if type_benne'))
    elif line.startswith('                    volume_benne = st.selectbox("Volume de la benne"'):
        new_lines.append(line.replace('                    volume_benne', '                volume_benne'))
    elif line.startswith('            with colB:'):
        new_lines.append(line.replace('            with', '        with'))
    elif line.startswith('                import datetime as dt'):
        new_lines.append(line.replace('                import', '            import'))
    elif line.startswith('                date_livraison = st.date_input("Date souhaitée"'):
        new_lines.append(line.replace('                date_livraison', '            date_livraison'))
    elif line.startswith('                est_valide = True'):
        new_lines.append(line.replace('                est_valide', '            est_valide'))
    elif line.startswith('                message_erreur = ""'):
        new_lines.append(line.replace('                message_erreur', '            message_erreur'))
    elif line.startswith('                try:'):
        new_lines.append(line.replace('                try', '            try'))
    elif line.startswith('                    est_valide, message_erreur = est_jour_ouvrable(date_livraison)'):
        new_lines.append(line.replace('                    est_valide', '                est_valide'))
    elif line.startswith('                except Exception:'):
        new_lines.append(line.replace('                except Exception', '            except Exception'))
    elif line.startswith('                    pass'):
        new_lines.append(line.replace('                    pass', '                pass'))
    elif line.startswith('                if not est_valide: st.error(f"⚠️'):
        new_lines.append(line.replace('                if not', '            if not'))
    elif line.startswith('                creneaux = ["Indifférent dans la journée"'):
        new_lines.append(line.replace('                creneaux', '            creneaux'))
    elif line.startswith('                creneau_choisi = st.selectbox("Créneau horaire"'):
        new_lines.append(line.replace('                creneau_choisi', '            creneau_choisi'))
    elif line.startswith('                instructions = st.text_area("Instructions spéciales'):
        new_lines.append(line.replace('                instructions', '            instructions'))
    elif line.startswith('            if st.button("✅ Valider et Enregistrer"'):
        new_lines.append(line.replace('            if st', '        if st'))
    elif line.startswith('                if selected_site_id == "NEW" and not new_site_address:'):
        new_lines.append(line.replace('                if selected', '            if selected'))
    elif line.startswith('                    st.error("⚠️'):
        new_lines.append(line.replace('                    st.error', '                st.error'))
    elif line.startswith('                else:'):
        new_lines.append(line.replace('                else:', '            else:'))
    elif line.startswith('                    try:'):
        new_lines.append(line.replace('                    try:', '                try:'))
    elif line.startswith('                        final_site_id = selected_site_id'):
        new_lines.append(line.replace('                        final', '                    final'))
    elif line.startswith('                        # Si c\'est un nouveau chantier'):
        new_lines.append(line.replace('                        #', '                    #'))
    elif line.startswith('                        if selected_site_id == "NEW":'):
        new_lines.append(line.replace('                        if', '                    if'))
    elif line.startswith('                            lbl = new_site_label'):
        new_lines.append(line.replace('                            lbl', '                        lbl'))
    elif line.startswith('                            res = run_query("""'):
        new_lines.append(line.replace('                            res', '                        res'))
    elif line.startswith('                                INSERT INTO sites'):
        new_lines.append(line.replace('                                INSERT', '                            INSERT'))
    elif line.startswith('                                VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id'):
        new_lines.append(line.replace('                                VALUES', '                            VALUES'))
    elif line.startswith('                            """, {"cid": selected_client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps}).fetchone()'):
        new_lines.append(line.replace('                            """,', '                        """,'))
    elif line.startswith('                            if res:'):
        new_lines.append(line.replace('                            if', '                        if'))
    elif line.startswith('                                final_site_id = res[0]'):
        new_lines.append(line.replace('                                final', '                            final'))
    elif line.startswith('                        insert_query = """'):
        new_lines.append(line.replace('                        insert_query', '                    insert_query'))
    elif line.startswith('                        INSERT INTO orders'):
        new_lines.append(line.replace('                        INSERT', '                    INSERT'))
    elif line.startswith('                        VALUES (:client_id, :site_id,'):
        new_lines.append(line.replace('                        VALUES', '                    VALUES'))
    elif line.startswith('                        """'):
        new_lines.append(line.replace('                        """', '                    """'))
    elif line.startswith('                        service_final = f"Benne - {action_benne}"'):
        new_lines.append(line.replace('                        service', '                    service'))
    elif line.startswith('                        run_query(insert_query, {'):
        new_lines.append(line.replace('                        run_query', '                    run_query'))
    elif line.startswith('                            "client_id": selected_client_id,'):
        new_lines.append(line.replace('                            "client', '                        "client'))
    elif line.startswith('                            "material": marchandise,'):
        new_lines.append(line.replace('                            "material', '                        "material'))
    elif line.startswith('                            "waste_type": type_benne,'):
        new_lines.append(line.replace('                            "waste', '                        "waste'))
    elif line.startswith('                        })'):
        new_lines.append(line.replace('                        })', '                    })'))
    elif line.startswith('                        st.success(f"🎉 Commande enregistrée'):
        new_lines.append(line.replace('                        st.success', '                    st.success'))
    elif line.startswith('                        # Note: pour afficher l\'alerte'):
        new_lines.append(line.replace('                        #', '                    #'))
    elif line.startswith('                        if selected_site_id == "NEW":'):
        new_lines.append(line.replace('                        if', '                    if'))
    elif line.startswith('                            st.success(f"📍 Le nouveau chantier'):
        new_lines.append(line.replace('                            st.success', '                        st.success'))
    elif line.startswith('                    except Exception as e:'):
        new_lines.append(line.replace('                    except', '                except'))
    elif line.startswith('                        st.error(f"Erreur'):
        new_lines.append(line.replace('                        st.error', '                    st.error'))
    else:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)
