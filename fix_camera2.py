import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

veh_old = """                    desc = st.text_area("Explication du problème", placeholder="Que se passe-t-il sur ce véhicule ?")
                    
                    import base64
                    photo_file = st.file_uploader("Prendre / Joindre une photo 📸", type=["jpg", "jpeg", "png"])
                    
                    submitted = st.form_submit_button("Envoyer le signalement 🚀", type="primary", use_container_width=True)
                    if submitted:
                        if veh_id and desc:
                            photo_b64 = ""
                            if photo_file is not None:
                                photo_b64 = base64.b64encode(photo_file.read()).decode()"""

veh_new = """                    desc = st.text_area("Explication du problème", placeholder="Que se passe-t-il sur ce véhicule ?")
                    
                    import base64
                    st.write("📸 Ajouter une photo")
                    c1, c2 = st.columns(2)
                    with c1:
                        photo_cam = st.camera_input("Caméra", key=f"cam_veh_{veh_id}")
                    with c2:
                        photo_file = st.file_uploader("Galerie", type=["jpg", "jpeg", "png"], key=f"file_veh_{veh_id}")
                    
                    submitted = st.form_submit_button("Envoyer le signalement 🚀", type="primary", use_container_width=True)
                    if submitted:
                        if veh_id and desc:
                            photo_b64 = ""
                            final_photo = photo_cam if photo_cam is not None else photo_file
                            if final_photo is not None:
                                photo_b64 = base64.b64encode(final_photo.read()).decode()"""

if veh_old in content:
    content = content.replace(veh_old, veh_new)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replacement done for vehicle.")
else:
    print("Pattern not found.")
