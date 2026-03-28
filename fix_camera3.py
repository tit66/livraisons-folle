import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

admin_old = """                import base64
                admin_photo_file = st.file_uploader("Prendre / Joindre une photo 📸", type=["jpg", "jpeg", "png"])
                
                admin_submitted = st.form_submit_button("Envoyer le signalement", type="primary")
                if admin_submitted:
                    if admin_veh_id and admin_desc:
                        admin_photo_b64 = ""
                        if admin_photo_file is not None:
                            admin_photo_b64 = base64.b64encode(admin_photo_file.read()).decode()"""

admin_new = """                import base64
                st.write("📸 Ajouter une photo")
                c1, c2 = st.columns(2)
                with c1:
                    admin_photo_cam = st.camera_input("Caméra", key="admin_cam")
                with c2:
                    admin_photo_file = st.file_uploader("Galerie", type=["jpg", "jpeg", "png"], key="admin_file")
                
                admin_submitted = st.form_submit_button("Envoyer le signalement", type="primary")
                if admin_submitted:
                    if admin_veh_id and admin_desc:
                        admin_photo_b64 = ""
                        final_admin_photo = admin_photo_cam if admin_photo_cam is not None else admin_photo_file
                        if final_admin_photo is not None:
                            admin_photo_b64 = base64.b64encode(final_admin_photo.read()).decode()"""

if admin_old in content:
    content = content.replace(admin_old, admin_new)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replacement done for admin.")
else:
    print("Pattern not found for admin.")
