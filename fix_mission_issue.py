import re

with open("app.py", "r") as f:
    content = f.read()

old_block = """                            if st.checkbox("❌ Signaler un problème", key=f"chk_issue_mission_{m['id']}"):
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
                                            )"""

new_block = """                            if st.checkbox("❌ Signaler un problème", key=f"chk_issue_mission_{m['id']}"):
                                with st.form(f"form_issue_mission_{m['id']}"):
                                    issue_desc = st.text_area("Explication du problème", placeholder="Que se passe-t-il sur le chantier ?")
                                    import base64
                                    issue_photo = st.file_uploader("Photo du problème 📸", type=["jpg", "jpeg", "png"])
                                    
                                    if st.form_submit_button("🚨 Envoyer l'alerte au bureau", type="primary", use_container_width=True):
                                        if issue_desc:
                                            pic_b64 = ""
                                            if issue_photo is not None:
                                                pic_b64 = base64.b64encode(issue_photo.read()).decode()
                                            
                                            run_query(
                                                "INSERT INTO order_issues (order_id, driver_id, description, photo_data) VALUES (:oid, :did, :desc, :pic)",
                                                {"oid": m['id'], "did": chauffeur_id, "desc": issue_desc, "pic": pic_b64}
                                            )"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Mission issue form simplified.")
else:
    print("Could not find mission issue form.")

with open("app.py", "w") as f:
    f.write(content)

