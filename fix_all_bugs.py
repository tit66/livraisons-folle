#!/usr/bin/env python3
import re

with open('app.py', 'r') as f:
    code = f.read()

original = code

# ─── Patch 1 : Suppression [STATUS] dans label expander du dashboard ───
# Déjà appliqué par le run précédent (vérifié)
if "[row['status'].upper()]" not in code:
    print("ℹ️  Patch 1 déjà appliqué")
else:
    code = re.sub(
        r"(f\"\{color_badge\} )\[\{row\['status'\]\.upper\(\)\}\] (\{row\['client_name'\])",
        r"\1\2",
        code
    )
    print("✅ Patch 1 : suppression [STATUS] dans expander dashboard")

# ─── Patch 2 : Taille benne + déchargement dans le dashboard (fc1 side) ───
# On cherche la ligne "new_qty = st.number_input..." dans le contexte du dashboard
# et on la remplace par la logique benne/livraison

old2 = """                    new_qty = st.number_input("⚖️ Quantité (tonnes)", value=float(row['quantity_tons'] or 0), min_value=0.0, step=0.5, key=f"qty_{order_id}")
                    with fc2:
                        # Material ou waste_type selon service_type
                        stype = str(row['service_type'] or "").lower()
                        if "benne" in stype:
                            new_material = None
                            new_waste = st.text_input("🗑️ Type de déchet", value=row['waste_type'] or "", key=f"waste_{order_id}")
                            # Point de déchargement
                            unload_val = row['unloading_point'] or ""
                            unload_idx = unloading_options.index(unload_val) if unload_val in unloading_options else 0
                            if unloading_options:
                                new_unload = st.selectbox("📍 Point de déchargement", unloading_options, index=unload_idx, key=f"unload_{order_id}")
                            else:
                                new_unload = st.text_input("📍 Point de déchargement", value=unload_val, key=f"unload_{order_id}")
                            new_load = row['loading_point'] or ""
                        else:
                            new_waste = None
                            new_material = st.text_input("📦 Matériau", value=row['material'] or "", key=f"mat_{order_id}")
                            # Point de chargement
                            load_val = row['loading_point'] or ""
                            load_idx = loading_options.index(load_val) if load_val in loading_options else 0
                            if loading_options:
                                new_load = st.selectbox("📍 Lieu de chargement", loading_options, index=load_idx, key=f"load_{order_id}")
                            else:
                                new_load = st.text_input("📍 Lieu de chargement", value=load_val, key=f"load_{order_id}")
                            new_unload = row['unloading_point'] or ""

                        drv_keys = list(drv_dict.keys())
                        curr_drv = row['driver_id'] if row['driver_id'] in drv_keys else None
                        drv_idx = drv_keys.index(curr_drv) if curr_drv in drv_keys else 0
                        new_driver = st.selectbox("👤 Chauffeur", drv_keys, format_func=lambda x: drv_dict[x], index=drv_idx, key=f"drv_{order_id}")

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("💾 Mettre à jour", key=f"upd_{order_id}", type="primary"):
                            run_query("""
                                UPDATE orders SET
                                    requested_date=:rd, requested_slot=:rs, quantity_tons=:qty,
                                    material=:mat, waste_type=:waste, driver_id=:did,
                                    loading_point=:lp, unloading_point=:up,
                                    updated_at=NOW()
                                WHERE id=:id
                            """, {
                                "rd": new_date, "rs": new_slot, "qty": new_qty,
                                "mat": new_material, "waste": new_waste, "did": new_driver,
                                "lp": new_load, "up": new_unload, "id": order_id
                            })"""

new2 = """                    # Détection type pour fc1
                    stype_edit = str(row['service_type'] or "").lower()
                    is_benne_edit = "benne" in stype_edit
                    if is_benne_edit:
                        df_inv_e = load_data("SELECT size FROM skip_inventory ORDER BY size")
                        inv_e_opts = df_inv_e['size'].tolist() if not df_inv_e.empty else []
                        curr_cont = str(row['container_type'] or "")
                        if inv_e_opts:
                            cont_idx = inv_e_opts.index(curr_cont) if curr_cont in inv_e_opts else 0
                            new_container = st.selectbox("📦 Taille de benne", inv_e_opts, index=cont_idx, key=f"cont_{order_id}")
                        else:
                            new_container = st.text_input("📦 Taille de benne", value=curr_cont, key=f"cont_{order_id}")
                        new_qty = float(row['quantity_tons'] or 0)
                    else:
                        new_container = str(row['container_type'] or "")
                        new_qty = st.number_input("⚖️ Quantité (tonnes)", value=float(row['quantity_tons'] or 0), min_value=0.0, step=0.5, key=f"qty_{order_id}")
                    with fc2:
                        if is_benne_edit:
                            new_material = None
                            new_waste = st.text_input("🗑️ Type de déchet", value=row['waste_type'] or "", key=f"waste_{order_id}")
                            # Point de déchargement
                            unload_val = row['unloading_point'] or ""
                            unload_idx = unloading_options.index(unload_val) if unload_val in unloading_options else 0
                            if unloading_options:
                                new_unload = st.selectbox("📍 Point de déchargement", unloading_options, index=unload_idx, key=f"unload_{order_id}")
                            else:
                                new_unload = st.text_input("📍 Point de déchargement", value=unload_val, key=f"unload_{order_id}")
                            new_load = row['loading_point'] or ""
                        else:
                            new_waste = None
                            new_material = st.text_input("📦 Matériau", value=row['material'] or "", key=f"mat_{order_id}")
                            # Point de chargement
                            load_val = row['loading_point'] or ""
                            load_idx = loading_options.index(load_val) if load_val in loading_options else 0
                            if loading_options:
                                new_load = st.selectbox("📍 Lieu de chargement", loading_options, index=load_idx, key=f"load_{order_id}")
                            else:
                                new_load = st.text_input("📍 Lieu de chargement", value=load_val, key=f"load_{order_id}")
                            new_unload = row['unloading_point'] or ""

                        drv_keys = list(drv_dict.keys())
                        curr_drv = row['driver_id'] if row['driver_id'] in drv_keys else None
                        drv_idx = drv_keys.index(curr_drv) if curr_drv in drv_keys else 0
                        new_driver = st.selectbox("👤 Chauffeur", drv_keys, format_func=lambda x: drv_dict[x], index=drv_idx, key=f"drv_{order_id}")

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("💾 Mettre à jour", key=f"upd_{order_id}", type="primary"):
                            run_query("""
                                UPDATE orders SET
                                    requested_date=:rd, requested_slot=:rs, quantity_tons=:qty,
                                    material=:mat, waste_type=:waste, driver_id=:did,
                                    loading_point=:lp, unloading_point=:up,
                                    container_type=:ct
                                WHERE id=:id
                            """, {
                                "rd": new_date, "rs": new_slot, "qty": new_qty,
                                "mat": new_material, "waste": new_waste, "did": new_driver,
                                "lp": new_load, "up": new_unload, "ct": new_container, "id": order_id
                            })"""

if old2 in code:
    code = code.replace(old2, new2, 1)
    print("✅ Patch 2 : benne = taille + déchargement dans le dashboard")
else:
    print("❌ Patch 2 non trouvé, vérification manuelle requise")
    # Debug : chercher une portion
    snippet = 'new_qty = st.number_input("⚖️ Quantité (tonnes)"'
    idx = code.find(snippet)
    if idx >= 0:
        print(f"   Snippet trouvé à l'offset {idx}")
        print(repr(code[idx-200:idx+50]))
    else:
        print("   Snippet introuvable")

# ─── Patch 3 : Planning - suppression [STATUS] dans les checkboxes ───
p3a_old = "f\"[{row['status'].upper()}] {row['client']} — {row['service_type']} — {row['details']} ({row['requested_slot']})\","
p3a_new = "f\"{row['client']} — {row['service_type']} — {row['details']} ({row['requested_slot']})\","
count3 = code.count(p3a_old)
if count3 > 0:
    code = code.replace(p3a_old, p3a_new)
    print(f"✅ Patch 3 : planning (suppression [STATUS] dans {count3} checkbox(es))")
else:
    print("ℹ️  Patch 3 déjà appliqué ou introuvable")

# ─── Patch 4 : Vue mobile - remplacer expander imbriqué ───
old4 = """                    with col_m2:
                        # 5c. Signalement problème livraison avec photo
                        with st.expander(L['report_issue']):
                            with st.form(f"mission_issue_{m['id']}"):
                                issue_desc = st.text_area("Décrivez le problème")
                                issue_photo_cam = st.camera_input("📸 Prendre une photo")
                                issue_photo_file = st.file_uploader("📎 Ou importer", type=["jpg", "jpeg", "png"], key=f"ph_{m['id']}")
                                if st.form_submit_button(L['send_alert'], type="primary", use_container_width=True):
                                    if issue_desc:
                                        pic_path = ""
                                        photo_src = issue_photo_cam or issue_photo_file
                                        if photo_src is not None:
                                            os.makedirs("uploads/photos", exist_ok=True)
                                            filename = f"{uuid.uuid4().hex}.jpg"
                                            filepath = os.path.join("uploads/photos", filename)
                                            with open(filepath, "wb") as f:
                                                f.write(photo_src.getbuffer())
                                            pic_path = filepath
                                        run_query(
                                            "INSERT INTO order_issues (order_id, driver_id, description, photo_data) VALUES (:oid, :did, :desc, :pic)",
                                            {"oid": m['id'], "did": chauffeur_id, "desc": issue_desc, "pic": pic_path}
                                        )
                                        st.success("🚨 Alerte envoyée au bureau !")
                                    else:
                                        st.error("La description est obligatoire.")"""

new4 = """                    with col_m2:
                        # 5c. Signalement problème (bouton toggle - sans expander imbriqué)
                        toggle_key = f"show_issue_{m['id']}"
                        if st.button(L['report_issue'], key=f"btn_issue_{m['id']}", use_container_width=True):
                            st.session_state[toggle_key] = not st.session_state.get(toggle_key, False)
                        if st.session_state.get(toggle_key, False):
                            with st.form(f"mission_issue_{m['id']}"):
                                issue_desc = st.text_area(L['issue_desc'])
                                issue_photo_cam = st.camera_input("📸 Prendre une photo")
                                issue_photo_file = st.file_uploader("📎 Ou importer", type=["jpg", "jpeg", "png"], key=f"ph_{m['id']}")
                                if st.form_submit_button(L['send_alert'], type="primary", use_container_width=True):
                                    if issue_desc:
                                        pic_path = ""
                                        photo_src = issue_photo_cam or issue_photo_file
                                        if photo_src is not None:
                                            os.makedirs("uploads/photos", exist_ok=True)
                                            filename = f"{uuid.uuid4().hex}.jpg"
                                            filepath = os.path.join("uploads/photos", filename)
                                            with open(filepath, "wb") as f:
                                                f.write(photo_src.getbuffer())
                                            pic_path = filepath
                                        run_query(
                                            "INSERT INTO order_issues (order_id, driver_id, description, photo_data) VALUES (:oid, :did, :desc, :pic)",
                                            {"oid": m['id'], "did": chauffeur_id, "desc": issue_desc, "pic": pic_path}
                                        )
                                        st.session_state[toggle_key] = False
                                        st.success("🚨 Alerte envoyée au bureau !")
                                    else:
                                        st.error("La description est obligatoire.")"""

if old4 in code:
    code = code.replace(old4, new4, 1)
    print("✅ Patch 4 : vue mobile (bouton toggle remplace expander imbriqué)")
else:
    print("❌ Patch 4 non trouvé")
    idx = code.find("with st.expander(L['report_issue'])")
    print(f"   Recherche expander mobile : offset={idx}")
    if idx > 0:
        print(repr(code[idx-200:idx+100]))

# ─── Patch 5 : Centre de tri - supprimer barres de progression ───
old5 = """                with col_info:
                    st.write(f"**{bin_row['bin_type']}** ({bin_row['container_size']}) — {status_label}")
                    st.progress(fill_ratio, text=f"{bin_row['bin_type']} — {int(fill_ratio * 100)}%")
                    if bin_row['notes']:
                        st.caption(f"Note : {bin_row['notes']}")"""
new5 = """                with col_info:
                    st.write(f"**{bin_row['bin_type']}** ({bin_row['container_size']}) — {status_label}")
                    if bin_row['notes']:
                        st.caption(f"Note : {bin_row['notes']}")"""

if old5 in code:
    code = code.replace(old5, new5, 1)
    print("✅ Patch 5 : centre de tri (suppression barres de progression)")
else:
    print("❌ Patch 5 non trouvé")
    idx = code.find("st.progress(fill_ratio")
    print(f"   Recherche progress bar : offset={idx}")

# Écriture finale
if code != original:
    with open('app.py', 'w') as f:
        f.write(code)
    print("\n✅ app.py mis à jour !")
else:
    print("\nℹ️  Aucun changement écrit (tous déjà appliqués)")
