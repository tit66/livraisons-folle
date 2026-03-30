NEW_PLANNING_BLOCK = '''\
    st.write(f"### 1️⃣ Planning du {date_planning.strftime('%d/%m/%Y')}")
    try:
        df_plan = load_data("""
            SELECT o.id, c.name as client, o.service_type, o.requested_slot,
                   COALESCE(o.material, o.waste_type) as details,
                   s.address, o.status,
                   o.driver_id,
                   COALESCE(o.delivery_order, 0) as delivery_order,
                   CONCAT(d.first_name, \' \', d.last_name) as chauffeur,
                   v.license_plate as vehicule
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN sites s ON o.site_id = s.id
            LEFT JOIN drivers d ON o.driver_id = d.id
            LEFT JOIN vehicles v ON o.vehicle_id = v.id
            WHERE o.requested_date = :d AND o.status IN (\'pending\', \'planned\', \'dispatched\')
            ORDER BY o.driver_id NULLS FIRST, COALESCE(o.delivery_order, 0), o.id
        """, {"d": date_planning})

        df_drivers_sel = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true")
        df_vehicles_sel = load_data("SELECT id, license_plate, name, type FROM vehicles WHERE is_available = true")

        drv_dict = {None: "--- Choisir un chauffeur ---"}
        for _, r in df_drivers_sel.iterrows():
            drv_dict[r["id"]] = f"{r['first_name']} {r['last_name']}"

        veh_dict_sel = {None: "--- Choisir un véhicule ---"}
        trailer_dict = {None: "Aucune remorque"}
        for _, r in df_vehicles_sel.iterrows():
            label = f"{r['license_plate']} ({r['type']}) {r['name'] or ''}"
            veh_dict_sel[r["id"]] = label
            trailer_dict[r["id"]] = label

        selected_order_ids = []
        if df_plan.empty:
            st.info("Aucune commande à planifier pour cette date.")
        else:
            unassigned = df_plan[df_plan["driver_id"].isna()]
            assigned = df_plan[df_plan["driver_id"].notna()]

            # ── Commandes non assignées ──
            if not unassigned.empty:
                st.write("#### 🔴 Non assignées")
                for _, row in unassigned.iterrows():
                    c_chk, c_info = st.columns([0.5, 9.5])
                    with c_chk:
                        checked = st.checkbox("", key=f"chk_{row['id']}", label_visibility="collapsed")
                    with c_info:
                        st.write(f"**{row['client']}** — {row['service_type']} — {row['details'] or ''} ({row['requested_slot'] or '?'})")
                    if checked:
                        selected_order_ids.append(row["id"])

            # ── Grouper par chauffeur ──
            if not assigned.empty:
                grouped_drivers = assigned.groupby("driver_id")
                for driver_id, group in grouped_drivers:
                    group = group.sort_values("delivery_order")
                    driver_name = group.iloc[0]["chauffeur"] or f"Chauffeur #{driver_id}"
                    with st.expander(f"👤 {driver_name} — {len(group)} mission(s)", expanded=True):
                        for pos, (_, row) in enumerate(group.iterrows()):
                            order_ids_list = group["id"].tolist()
                            c_num, c_chk, c_label, c_up, c_dn, c_reassign, c_unassign = st.columns([0.5, 0.5, 6, 0.5, 0.5, 1.5, 1.5])
                            with c_num:
                                st.markdown(f"**#{pos+1}**")
                            with c_chk:
                                checked = st.checkbox("", key=f"chk_{row['id']}", label_visibility="collapsed")
                            with c_label:
                                st.write(f"**{row['client']}** — {row['service_type']} — {row['details'] or ''} ({row['requested_slot'] or '?'})")
                            # Bouton monter
                            with c_up:
                                if pos > 0:
                                    if st.button("⬆️", key=f"up_{row['id']}", help="Monter dans la tournée"):
                                        prev_id = order_ids_list[pos - 1]
                                        run_query("UPDATE orders SET delivery_order=:o WHERE id=:id", {"o": pos - 1, "id": row["id"]})
                                        run_query("UPDATE orders SET delivery_order=:o WHERE id=:id", {"o": pos, "id": prev_id})
                                        st.cache_data.clear()
                                        st.rerun()
                            # Bouton descendre
                            with c_dn:
                                if pos < len(group) - 1:
                                    if st.button("⬇️", key=f"dn_{row['id']}", help="Descendre dans la tournée"):
                                        next_id = order_ids_list[pos + 1]
                                        run_query("UPDATE orders SET delivery_order=:o WHERE id=:id", {"o": pos + 1, "id": row["id"]})
                                        run_query("UPDATE orders SET delivery_order=:o WHERE id=:id", {"o": pos, "id": next_id})
                                        st.cache_data.clear()
                                        st.rerun()
                            # Réassigner à un autre chauffeur
                            with c_reassign:
                                other_drivers = {k: v for k, v in drv_dict.items() if k != driver_id and k is not None}
                                if other_drivers:
                                    reassign_target = st.selectbox(
                                        "↪️ Réassigner",
                                        options=[None] + list(other_drivers.keys()),
                                        format_func=lambda x: "↪️ Réassigner..." if x is None else other_drivers.get(x, ""),
                                        key=f"reassign_sel_{row['id']}",
                                        label_visibility="collapsed"
                                    )
                                    if reassign_target is not None:
                                        # Compter les missions du nouveau chauffeur ce jour-là
                                        df_new_drv = df_plan[df_plan["driver_id"] == reassign_target]
                                        new_order = len(df_new_drv)
                                        run_query(
                                            "UPDATE orders SET driver_id=:did, delivery_order=:o WHERE id=:id",
                                            {"did": reassign_target, "o": new_order, "id": row["id"]}
                                        )
                                        st.cache_data.clear()
                                        st.rerun()
                            # Remettre en attente
                            with c_unassign:
                                if st.button("🔄 Attente", key=f"unassign_{row['id']}", help="Désassigner et remettre en attente"):
                                    run_query(
                                        "UPDATE orders SET status=\'pending\', driver_id=NULL, vehicle_id=NULL, trailer_id=NULL, delivery_order=0 WHERE id=:id",
                                        {"id": row["id"]}
                                    )
                                    st.cache_data.clear()
                                    st.rerun()
                            if checked:
                                selected_order_ids.append(row["id"])

        st.markdown("---")
        st.write("### 2️⃣ Assigner les ressources à la sélection")
        c_as1, c_as2, c_as3 = st.columns(3)
        with c_as1:
            assign_driver = st.selectbox("Chauffeur", options=list(drv_dict.keys()), format_func=lambda x: drv_dict[x])
        with c_as2:
            assign_vehicle = st.selectbox("Véhicule", options=list(veh_dict_sel.keys()), format_func=lambda x: veh_dict_sel[x])
        with c_as3:
            assign_trailer = st.selectbox("Remorque (optionnel)", options=list(trailer_dict.keys()), format_func=lambda x: trailer_dict[x])

        if st.button("💾 Assigner la sélection", type="primary"):
            if not selected_order_ids:
                st.warning("Aucune commande sélectionnée.")
            else:
                # Calculer le delivery_order de départ pour ce chauffeur
                df_existing = df_plan[df_plan["driver_id"] == assign_driver] if assign_driver else pd.DataFrame()
                start_order = len(df_existing)
                for i_ord, oid in enumerate(selected_order_ids):
                    run_query("""
                        UPDATE orders SET status=\'planned\', driver_id=:did, vehicle_id=:vid, trailer_id=:tid, delivery_order=:o
                        WHERE id=:oid
                    """, {"did": assign_driver, "vid": assign_vehicle, "tid": assign_trailer, "o": start_order + i_ord, "oid": oid})
                st.success(f"✅ {len(selected_order_ids)} commande(s) assignée(s).")
                st.cache_data.clear()
                st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")
'''
