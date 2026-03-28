import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix for Vehicle Issues
veh_old = """                    desc = st.text_area("Explication du problème", placeholder="Que se passe-t-il sur ce véhicule ?")
                    
                    import base64
                    photo_file = st.file_uploader("Prendre / Joindre une photo 📸", type=["jpg", "jpeg", "png"])
                    
                    submitted = st.form_submit_button("Envoyer le signalement 🚀", type="primary", use_container_width=True)
                    if submitted:
                        if desc:
                            photo_b64 = ""
                            if photo_file is not None:
                                photo_b64 = base64.b64encode(photo_file.read()).decode()"""

veh_new = """                    desc = st.text_area("Explication du problème", placeholder="Que se passe-t-il sur ce véhicule ?")
                    
                    import base64
                    st.write("📸 Ajouter une photo (Caméra directe ou Galerie)")
                    c1, c2 = st.columns(2)
                    with c1:
                        photo_cam = st.camera_input("Prendre une photo en direct")
                    with c2:
                        photo_file = st.file_uploader("Ou choisir dans la galerie", type=["jpg", "jpeg", "png"])
                    
                    submitted = st.form_submit_button("Envoyer le signalement 🚀", type="primary", use_container_width=True)
                    if submitted:
                        if desc:
                            photo_b64 = ""
                            final_photo = photo_cam if photo_cam is not None else photo_file
                            if final_photo is not None:
                                photo_b64 = base64.b64encode(final_photo.read()).decode()"""

content = content.replace(veh_old, veh_new)

# Fix for Mission Issues
mis_old = """                                    issue_desc = st.text_area("Explication du problème", placeholder="Que se passe-t-il sur le chantier ?")
                                    import base64
                                    issue_photo = st.file_uploader("Photo du problème 📸", type=["jpg", "jpeg", "png"])
                                    
                                    if st.form_submit_button("🚨 Envoyer l'alerte au bureau", type="primary", use_container_width=True):
                                        if issue_desc:
                                            pic_b64 = ""
                                            if issue_photo is not None:
                                                pic_b64 = base64.b64encode(issue_photo.read()).decode()"""

mis_new = """                                    issue_desc = st.text_area("Explication du problème", placeholder="Que se passe-t-il sur le chantier ?")
                                    import base64
                                    st.write("📸 Ajouter une photo du problème")
                                    c_cam, c_gal = st.columns(2)
                                    with c_cam:
                                        issue_cam = st.camera_input("Caméra directe", key=f"cam_issue_{m['id']}")
                                    with c_gal:
                                        issue_photo = st.file_uploader("Galerie", type=["jpg", "jpeg", "png"], key=f"file_issue_{m['id']}")
                                    
                                    if st.form_submit_button("🚨 Envoyer l'alerte au bureau", type="primary", use_container_width=True):
                                        if issue_desc:
                                            pic_b64 = ""
                                            final_issue_photo = issue_cam if issue_cam is not None else issue_photo
                                            if final_issue_photo is not None:
                                                pic_b64 = base64.b64encode(final_issue_photo.read()).decode()"""

content = content.replace(mis_old, mis_new)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement done.")
