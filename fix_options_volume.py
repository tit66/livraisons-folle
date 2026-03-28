import re

with open("app.py", "r") as f:
    content = f.read()

old_block = """            elif prestation == "Location de benne":
                action_benne = st.radio("Type d'intervention", ["Pose", "Rotation", "Enlèvement", "Déplacement sur chantier"], horizontal=True)
                type_benne = st.selectbox("Type de déchets", ["Gravats", "DIB (Tout venant)", "Déchets verts", "Bois"])
                options_volume = ["8m3", "10m3"] if type_benne == "Gravats" else ["8m3", "10m3", "15m3", "30m3"]
                if type_benne == "Gravats": st.caption("⚠️ Pour les gravats, le volume maximum est de 10m3 (limite de poids).")
                volume_benne = st.selectbox("Volume de la benne", options_volume)"""

new_block = """            elif prestation == "Location de benne":
                action_benne = st.radio("Type d'intervention", ["Pose", "Rotation", "Enlèvement", "Déplacement sur chantier"], horizontal=True)
                type_benne = st.selectbox("Type de déchets", ["Gravats", "DIB (Tout venant)", "Déchets verts", "Bois"])
                
                # Fetch available sizes from database dynamically
                df_sizes = load_data("SELECT size FROM skip_inventory ORDER BY size")
                all_sizes = df_sizes['size'].tolist() if not df_sizes.empty else ["8m3", "10m3", "15m3", "30m3"]
                
                # Filter for Gravats (try to parse number, hide if > 10)
                options_volume = []
                for s in all_sizes:
                    if type_benne == "Gravats":
                        match = re.search(r'\d+', s)
                        if match and int(match.group()) > 10:
                            continue
                    options_volume.append(s)
                
                if type_benne == "Gravats": st.caption("⚠️ Pour les gravats, le volume maximum conseillé est de 10m3 (limite de poids de sécurité).")
                volume_benne = st.selectbox("Volume de la benne", options_volume if options_volume else all_sizes)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Prestation block updated.")
else:
    print("Could not find the prestation block.")

with open("app.py", "w") as f:
    f.write(content)

