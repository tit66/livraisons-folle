import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Update the Mobile driver view for mission loop
old_mobile_mission_block = """                        if m['status'] != 'done':
                            if st.button("✅ Marquer comme TERMINÉ", key=f"btn_done_{m['id']}"):
                                run_query("UPDATE orders SET status='done' WHERE id=:oid", {"oid": m['id']})
                                st.rerun()
                        else:
                            st.success("Mission terminée !")"""

new_mobile_mission_block = """                        if m['status'] not in ['done', 'issue']:
                            c_btn_done, c_btn_issue = st.columns(2)
                            with c_btn_done:
                                if st.button("✅ TERMINÉ", key=f"btn_done_{m['id']}", use_container_width=True):
                                    run_query("UPDATE orders SET status='done' WHERE id=:oid", {"oid": m['id']})
                                    st.rerun()
                            
                            with st.expander("❌ Signaler un problème"):
                                with st.form(f"form_issue_mission_{m['id']}"):
                                    issue_reason = st.selectbox("Raison", ["Accès impossible / trop étroit", "Client absent / Portail fermé", "Mauvais déchets (ex: DIB au lieu de gravats)", "Surcharge", "Autre"])
                                    issue_desc = st.text_area("Explication détaillée", placeholder="Précisez le problème...")
                                    import base64
                                    issue_photo = st.file_uploader("Photo du problème 📸", type=["jpg", "jpeg", "png"])
                                    
                                    if st.form_submit_button("🚨 Envoyer l'alerte au bureau", type="primary", use_container_width=True):
                                        if issue_desc:
                                            pic_b64 = ""
                                            if issue_photo is not None:
                                                pic_b64 = base64.b64encode(issue_photo.read()).decode()
                                            
                                            run_query(
                                                "INSERT INTO order_issues (order_id, driver_id, description, photo_data) VALUES (:oid, :did, :desc, :pic)",
                                                {"oid": m['id'], "did": chauffeur_id, "desc": f"[{issue_reason}] {issue_desc}", "pic": pic_b64}
                                            )
                                            run_query("UPDATE orders SET status='issue' WHERE id=:oid", {"oid": m['id']})
                                            st.success("✅ Alerte envoyée !")
                                            st.rerun()
                                        else:
                                            st.error("⚠️ L'explication est obligatoire.")
                                            
                        elif m['status'] == 'issue':
                            st.error("❌ Problème signalé. En attente de traitement par le bureau.")
                        else:
                            st.success("✅ Mission terminée !")"""

if old_mobile_mission_block in content:
    content = content.replace(old_mobile_mission_block, new_mobile_mission_block)
    print("Mobile mission block updated successfully.")
else:
    print("Could not find mobile mission block.")

# 2. Add the Dashboard widget for Order Issues
old_dash_end = """                if st.button("✅ Marquer comme Résolu", key=f"resolve_issue_{row['id']}"):
                    run_query("UPDATE vehicle_issues SET is_resolved = true WHERE id = :id", {"id": row['id']})
                    st.rerun()"""

new_dash_end = """                if st.button("✅ Marquer comme Résolu", key=f"resolve_issue_{row['id']}"):
                    run_query("UPDATE vehicle_issues SET is_resolved = true WHERE id = :id", {"id": row['id']})
                    st.rerun()
                    
    # ALERTES PROBLEMES MISSIONS (CHANTIER)
    df_order_issues = load_data(\"\"\"
        SELECT oi.id, oi.order_id, d.first_name, d.last_name, c.name as client_name, 
               o.service_type, oi.description, oi.created_at, oi.photo_data 
        FROM order_issues oi 
        JOIN orders o ON oi.order_id = o.id 
        LEFT JOIN drivers d ON oi.driver_id = d.id 
        LEFT JOIN clients c ON o.client_id = c.id
        WHERE oi.is_resolved = false 
        ORDER BY oi.created_at DESC
    \"\"\")
    
    if not df_order_issues.empty:
        st.divider()
        st.error("### 🚨 Problèmes signalés sur chantier (Livraisons/Bennes)")
        for idx, row in df_order_issues.iterrows():
            date_str = pd.to_datetime(row['created_at']).strftime('%d/%m/%Y %H:%M')
            nom_signaleur = f"{row['first_name']} {row['last_name']}" if pd.notna(row['first_name']) else "Chauffeur inconnu"
            
            with st.expander(f"🛑 Mission {row['service_type']} chez {row['client_name']} - Signalé par {nom_signaleur} le {date_str}", expanded=True):
                st.write(f"**Description du problème :** {row['description']}")
                
                if pd.notna(row['photo_data']) and row['photo_data'].strip() != "":
                    import base64
                    st.image(base64.b64decode(row['photo_data']), caption="Preuve (Photo)", width=300)
                
                st.write("---")
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if st.button("🔄 Traiter et Replanifier (Remettre 'En Attente')", key=f"resolve_oissue_pending_{row['id']}", use_container_width=True):
                        run_query("UPDATE order_issues SET is_resolved = true WHERE id = :id", {"id": row['id']})
                        run_query("UPDATE orders SET status = 'pending', driver_id = NULL, vehicle_id = NULL, trailer_id = NULL WHERE id = :oid", {"oid": row['order_id']})
                        st.rerun()
                with c_act2:
                    if st.button("❌ Annuler définitivement la commande", key=f"resolve_oissue_cancel_{row['id']}", use_container_width=True):
                        run_query("UPDATE order_issues SET is_resolved = true WHERE id = :id", {"id": row['id']})
                        run_query("UPDATE orders SET status = 'cancelled' WHERE id = :oid", {"oid": row['order_id']})
                        st.rerun()"""

if old_dash_end in content:
    content = content.replace(old_dash_end, new_dash_end)
    print("Dashboard order issues widget updated successfully.")
else:
    print("Could not find dashboard end block.")

with open("app.py", "w") as f:
    f.write(content)

