import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target_block = """                # Fallback to single queries if IN clause fails with UUIDs
                preview_data = []
                for a in st.session_state["ai_proposal"]:
                    o_id = a.get("order_id")
                    if o_id:
                        df_single_o = load_data("SELECT o.id, c.name, o.service_type, o.dropoff_address FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.id = :oid", {"oid": o_id})
                        
                        client_name = df_single_o.iloc[0]['name'] if not df_single_o.empty else "Client Inconnu"
                        service_type = df_single_o.iloc[0]['service_type'] if not df_single_o.empty else "Type Inconnu"
                        
                        address = df_single_o.iloc[0]['dropoff_address'] if not df_single_o.empty and pd.notna(df_single_o.iloc[0]['dropoff_address']) else "Inconnue"
                        preview_data.append({
                            "Client & Mission": f"{client_name} - {service_type}",
                            "📍 Lieu": address,
                            "👨‍✈️ Chauffeur": dict_d.get(str(a.get("driver_id")), "Non assigné"),
                            "🚚 Camion": dict_v.get(str(a.get("vehicle_id")), "Non assigné")
                        })
                
                if preview_data:
                    import pandas as pd
                    st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)"""

# In case the dictionary `.get` in the original has `str(...)` or not (I used `dict_d.get(a.get("driver_id")` previously but I also ran `fix_ai_table_keys.py` so let's use a regex to be safe).

# Let's write a robust regex to find the preview_data generation block and replace it.
pattern = re.compile(r'# Fallback to single queries if IN clause fails with UUIDs.*?if preview_data:.*?st\.dataframe\(pd\.DataFrame\(preview_data\), use_container_width=True, hide_index=True\)', re.DOTALL)

new_block = """# Extraction et formatage des données
                preview_data = []
                for a in st.session_state["ai_proposal"]:
                    o_id = a.get("order_id")
                    if o_id:
                        query_o = "SELECT o.id, c.name, o.service_type, o.dropoff_address, o.material, o.waste_type, o.container_type, o.quantity_tons FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.id = :oid"
                        df_single_o = load_data(query_o, {"oid": o_id})
                        
                        if not df_single_o.empty:
                            row = df_single_o.iloc[0]
                            client_name = row['name'] if pd.notna(row['name']) else "Client Inconnu"
                            service_type = row['service_type'] if pd.notna(row['service_type']) else "Type Inconnu"
                            address = row['dropoff_address'] if pd.notna(row['dropoff_address']) else "Inconnue"
                            
                            # Construction du détail (Matériau ou type de benne)
                            detail = ""
                            if service_type == 'livraison' and pd.notna(row['material']):
                                qty = f"{row['quantity_tons']} T" if pd.notna(row['quantity_tons']) else ""
                                detail = f"📦 {row['material']} ({qty})"
                            elif service_type in ['pose', 'retrait', 'rotation']:
                                w_type = row['waste_type'] if pd.notna(row['waste_type']) else "DIB"
                                c_type = row['container_type'] if pd.notna(row['container_type']) else "Benne standard"
                                detail = f"🗑️ {c_type} - {w_type}"
                            
                            driver_id = str(a.get("driver_id", ""))
                            vehicle_id = str(a.get("vehicle_id", ""))
                            
                            preview_data.append({
                                "👨‍✈️ Chauffeur": dict_d.get(driver_id, "Non assigné"),
                                "Client & Mission": f"{client_name} - {service_type.upper()}",
                                "Détails (Produit/Benne)": detail,
                                "📍 Lieu": address,
                                "🚚 Camion": dict_v.get(vehicle_id, "Non assigné")
                            })
                
                if preview_data:
                    import pandas as pd
                    df_preview = pd.DataFrame(preview_data)
                    # Tri par chauffeur pour regrouper les tournées
                    df_preview = df_preview.sort_values(by=["👨‍✈️ Chauffeur", "Client & Mission"])
                    st.dataframe(df_preview, use_container_width=True, hide_index=True)"""

if pattern.search(content):
    content = pattern.sub(new_block, content)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Table formatting updated.")
else:
    print("Pattern not found. Checking if it's there.")
