import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Update the Dashboard Query to handle NULL driver_id (LEFT JOIN)
old_dash_query = "SELECT vi.id, d.first_name, d.last_name, v.license_plate, vi.description, vi.created_at, vi.photo_data FROM vehicle_issues vi JOIN drivers d ON vi.driver_id = d.id JOIN vehicles v ON vi.vehicle_id = v.id WHERE vi.is_resolved = false ORDER BY vi.created_at DESC"
new_dash_query = "SELECT vi.id, d.first_name, d.last_name, v.license_plate, vi.description, vi.created_at, vi.photo_data FROM vehicle_issues vi LEFT JOIN drivers d ON vi.driver_id = d.id JOIN vehicles v ON vi.vehicle_id = v.id WHERE vi.is_resolved = false ORDER BY vi.created_at DESC"
content = content.replace(old_dash_query, new_dash_query)

# Update Dashboard Display logic for Admin reports
old_dash_expander = "with st.expander(f\"⚠️ {row['license_plate']} - Signalé par {row['first_name']} {row['last_name']} le {date_str}\", expanded=True):"
new_dash_expander = """nom_signaleur = f"{row['first_name']} {row['last_name']}" if pd.notna(row['first_name']) else "Admin"
            with st.expander(f"⚠️ {row['license_plate']} - Signalé par {nom_signaleur} le {date_str}", expanded=True):"""
content = content.replace(old_dash_expander, new_dash_expander)


# 2. Add Admin Issue Form to Flotte
admin_issue_block = """
    st.divider()
    st.write("### 🚨 Signaler un problème véhicule (Admin)")
    df_all_veh_admin = load_data("SELECT id, license_plate, name, type FROM vehicles WHERE is_available = true")
    if not df_all_veh_admin.empty:
        veh_admin_dict = dict(zip(df_all_veh_admin['id'], df_all_veh_admin['license_plate'] + " - " + df_all_veh_admin['type'] + " (" + df_all_veh_admin['name'].fillna('') + ")"))
        keys_admin_list = [None] + list(veh_admin_dict.keys())
        
        with st.expander("Ouvrir le formulaire de signalement Admin"):
            with st.form("admin_issue_form"):
                admin_veh_id = st.selectbox("Véhicule concerné :", options=keys_admin_list, format_func=lambda x: "--- Choisir un véhicule ---" if x is None else veh_admin_dict[x])
                admin_desc = st.text_area("Explication libre du problème")
                
                import base64
                admin_photo_file = st.file_uploader("Prendre / Joindre une photo 📸", type=["jpg", "jpeg", "png"])
                
                admin_submitted = st.form_submit_button("Envoyer le signalement", type="primary")
                if admin_submitted:
                    if admin_veh_id and admin_desc:
                        admin_photo_b64 = ""
                        if admin_photo_file is not None:
                            admin_photo_b64 = base64.b64encode(admin_photo_file.read()).decode()
                            
                        run_query(
                            "INSERT INTO vehicle_issues (vehicle_id, description, photo_data) VALUES (:vid, :desc, :pic)",
                            {"vid": admin_veh_id, "desc": "[Signalement Admin] " + admin_desc, "pic": admin_photo_b64}
                        )
                        st.success("✅ Problème signalé !")
                        st.rerun()
                    else:
                        st.error("⚠️ Le véhicule et l'explication sont obligatoires.")

"""
# Inject right before mobile block
content = content.replace('elif navigation == "📱 Vue Chauffeur (Mobile)":', admin_issue_block + 'elif navigation == "📱 Vue Chauffeur (Mobile)":')


# 3. Simplify Mobile Driver View
# Since string replace over multi-line with dynamic content can be brittle, let's use regex
pattern_mobile = re.compile(r'def issue_form\(veh_id, form_key\):(.*?)st\.divider\(\)', re.DOTALL)

new_mobile = """def issue_form(veh_id, form_key):
                with st.form(form_key):
                    desc = st.text_area("Explication du problème", placeholder="Que se passe-t-il sur ce véhicule ?")
                    
                    import base64
                    photo_file = st.file_uploader("Prendre / Joindre une photo 📸", type=["jpg", "jpeg", "png"])
                    
                    submitted = st.form_submit_button("Envoyer le signalement 🚀", type="primary", use_container_width=True)
                    if submitted:
                        if veh_id and desc:
                            photo_b64 = ""
                            if photo_file is not None:
                                photo_b64 = base64.b64encode(photo_file.read()).decode()
                                
                            run_query(
                                "INSERT INTO vehicle_issues (driver_id, vehicle_id, description, photo_data) VALUES (:did, :vid, :desc, :pic)",
                                {"did": chauffeur_id, "vid": veh_id, "desc": desc, "pic": photo_b64}
                            )
                            st.success("✅ Problème signalé et transmis au bureau !")
                            st.rerun()
                        else:
                            st.error("⚠️ L'explication est obligatoire.")

            assigned_trailer_id = None
            if not df_assigned.empty and pd.notna(df_assigned.iloc[0]['t_id']):
                assigned_trailer_id = df_assigned.iloc[0]['t_id']

            if assigned_truck_id:
                with st.expander(f"🚛 Camion : {assigned_truck_label}"):
                    issue_form(assigned_truck_id, "form_truck")
                if assigned_trailer_label:
                    with st.expander(f"🔗 Remorque : {assigned_trailer_label}"):
                        issue_form(assigned_trailer_id, "form_trailer")
            else:
                st.warning("Aucun véhicule assigné automatiquement aujourd'hui.")
                
            st.divider()"""

content = pattern_mobile.sub(new_mobile, content)

with open("app.py", "w") as f:
    f.write(content)

