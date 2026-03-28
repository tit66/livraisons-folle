import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add os module if missing
if 'import os' not in content:
    content = content.replace('import pandas as pd', 'import os\nimport pandas as pd')

# Fix Admin Vehicle Issue
admin_old = """                if admin_submitted:
                    if admin_veh_id and admin_desc:
                        admin_photo_b64 = ""
                        final_admin_photo = admin_photo_cam if admin_photo_cam is not None else admin_photo_file
                        if final_admin_photo is not None:
                            admin_photo_b64 = base64.b64encode(final_admin_photo.read()).decode()
                            
                        run_query(
                            "INSERT INTO vehicle_issues (vehicle_id, description, photo_data) VALUES (:vid, :desc, :pic)",
                            {"vid": admin_veh_id, "desc": "[Signalement Admin] " + admin_desc, "pic": admin_photo_b64}
                        )"""

admin_new = """                if admin_submitted:
                    if admin_veh_id and admin_desc:
                        admin_photo_path = ""
                        final_admin_photo = admin_photo_cam if admin_photo_cam is not None else admin_photo_file
                        if final_admin_photo is not None:
                            os.makedirs("uploads/photos", exist_ok=True)
                            import uuid
                            filename = f"{uuid.uuid4().hex}.jpg"
                            filepath = os.path.join("uploads/photos", filename)
                            with open(filepath, "wb") as f:
                                f.write(final_admin_photo.getbuffer())
                            admin_photo_path = filepath
                            
                        run_query(
                            "INSERT INTO vehicle_issues (vehicle_id, description, photo_data) VALUES (:vid, :desc, :pic)",
                            {"vid": admin_veh_id, "desc": "[Signalement Admin] " + admin_desc, "pic": admin_photo_path}
                        )"""

if admin_old in content:
    content = content.replace(admin_old, admin_new)
    print("Admin storage fixed.")

# Fix Driver Vehicle Issue
driver_old = """                    if submitted:
                        if veh_id and desc:
                            photo_b64 = ""
                            final_photo = photo_cam if photo_cam is not None else photo_file
                            if final_photo is not None:
                                photo_b64 = base64.b64encode(final_photo.read()).decode()
                                
                            run_query(
                                "INSERT INTO vehicle_issues (driver_id, vehicle_id, description, photo_data) VALUES (:did, :vid, :desc, :pic)",
                                {"did": chauffeur_id, "vid": veh_id, "desc": desc, "pic": photo_b64}
                            )"""

driver_new = """                    if submitted:
                        if veh_id and desc:
                            photo_path = ""
                            final_photo = photo_cam if photo_cam is not None else photo_file
                            if final_photo is not None:
                                os.makedirs("uploads/photos", exist_ok=True)
                                import uuid
                                filename = f"{uuid.uuid4().hex}.jpg"
                                filepath = os.path.join("uploads/photos", filename)
                                with open(filepath, "wb") as f:
                                    f.write(final_photo.getbuffer())
                                photo_path = filepath
                                
                            run_query(
                                "INSERT INTO vehicle_issues (driver_id, vehicle_id, description, photo_data) VALUES (:did, :vid, :desc, :pic)",
                                {"did": chauffeur_id, "vid": veh_id, "desc": desc, "pic": photo_path}
                            )"""

if driver_old in content:
    content = content.replace(driver_old, driver_new)
    print("Driver storage fixed.")

# Fix Mission Issue
mission_old = """                                    if st.form_submit_button("🚨 Envoyer l'alerte au bureau", type="primary", use_container_width=True):
                                        if issue_desc:
                                            pic_b64 = ""
                                            final_issue_photo = issue_cam if issue_cam is not None else issue_photo
                                            if final_issue_photo is not None:
                                                pic_b64 = base64.b64encode(final_issue_photo.read()).decode()
                                            
                                            run_query(
                                                "INSERT INTO order_issues (order_id, driver_id, description, photo_data) VALUES (:oid, :did, :desc, :pic)",
                                                {"oid": m['id'], "did": chauffeur_id, "desc": issue_desc, "pic": pic_b64}
                                            )"""

mission_new = """                                    if st.form_submit_button("🚨 Envoyer l'alerte au bureau", type="primary", use_container_width=True):
                                        if issue_desc:
                                            pic_path = ""
                                            final_issue_photo = issue_cam if issue_cam is not None else issue_photo
                                            if final_issue_photo is not None:
                                                os.makedirs("uploads/photos", exist_ok=True)
                                                import uuid
                                                filename = f"{uuid.uuid4().hex}.jpg"
                                                filepath = os.path.join("uploads/photos", filename)
                                                with open(filepath, "wb") as f:
                                                    f.write(final_issue_photo.getbuffer())
                                                pic_path = filepath
                                            
                                            run_query(
                                                "INSERT INTO order_issues (order_id, driver_id, description, photo_data) VALUES (:oid, :did, :desc, :pic)",
                                                {"oid": m['id'], "did": chauffeur_id, "desc": issue_desc, "pic": pic_path}
                                            )"""

if mission_old in content:
    content = content.replace(mission_old, mission_new)
    print("Mission storage fixed.")

# Fix Image Display (Vehicle Issues)
display_old = """                if pd.notna(row['photo_data']) and row['photo_data'].strip() != "":
                    import base64
                    st.image(base64.b64decode(row['photo_data']), caption="Photo du problème", width=300)"""

display_new = """                if pd.notna(row['photo_data']) and row['photo_data'].strip() != "":
                    if row['photo_data'].startswith("uploads/"):
                        import os
                        if os.path.exists(row['photo_data']):
                            st.image(row['photo_data'], caption="Photo du problème", width=300)
                    else:
                        try:
                            import base64
                            st.image(base64.b64decode(row['photo_data']), caption="Photo du problème", width=300)
                        except:
                            pass"""

if display_old in content:
    content = content.replace(display_old, display_new)
    print("Display storage fixed for vehicle issues.")

# Fix Image Display (Mission Issues)
display_mission_old = """                if pd.notna(row['photo_data']) and row['photo_data'].strip() != "":
                    import base64
                    st.image(base64.b64decode(row['photo_data']), caption="Preuve (Photo)", width=300)"""

display_mission_new = """                if pd.notna(row['photo_data']) and row['photo_data'].strip() != "":
                    if row['photo_data'].startswith("uploads/"):
                        import os
                        if os.path.exists(row['photo_data']):
                            st.image(row['photo_data'], caption="Preuve (Photo)", width=300)
                    else:
                        try:
                            import base64
                            st.image(base64.b64decode(row['photo_data']), caption="Preuve (Photo)", width=300)
                        except:
                            pass"""

if display_mission_old in content:
    content = content.replace(display_mission_old, display_mission_new)
    print("Display storage fixed for mission issues.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
