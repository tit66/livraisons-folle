import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the IDs string construction
old_ids_line = "ids = ','.join([f\"'{a.get('order_id', '')}'\" for a in st.session_state['ai_proposal']])"
new_ids_line = "ids = ','.join([f\"'{a.get('order_id', '')}'\" for a in st.session_state['ai_proposal']])"

# And importantly, fix the dictionary unpacking. 
# The issue is `a.get("order_id")` because `st.session_state["ai_proposal"]` is weird in the user's debug output.
# Actually, the user's output looks like standard JSON parsed into a python list of dicts.
# The bug might be that `df_o` is empty because of quotes, or because of how pandas handles UUIDs in `IN` clause.

# Let's replace the whole preview loop with something robust that doesn't rely on the IN clause which is failing.
target_block = """                ids = ','.join([f"'{a.get('order_id', '')}'" for a in st.session_state['ai_proposal']])
                df_o = load_data(f"SELECT o.id, c.name, o.service_type, o.dropoff_address FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.id IN ({ids})") if ids else pd.DataFrame()
                
                preview_data = []
                for a in st.session_state["ai_proposal"]:
                    o_id = a.get("order_id")
                    if not df_o.empty and o_id in df_o['id'].values:
                        order_info = df_o[df_o['id'] == o_id].iloc[0]
                        preview_data.append({
                            "Commande N°": o_id,
                            "Client": order_info['name'],
                            "Type": order_info['service_type'],
                            "Chauffeur Prévu": dict_d.get(a.get("driver_id"), "Inconnu"),
                            "Camion Prévu": dict_v.get(a.get("vehicle_id"), "Inconnu")
                        })
                
                if preview_data:
                    import pandas as pd
                    st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)"""

new_block = """                # Fallback to single queries if IN clause fails with UUIDs
                preview_data = []
                for a in st.session_state["ai_proposal"]:
                    o_id = a.get("order_id")
                    if o_id:
                        df_single_o = load_data("SELECT o.id, c.name, o.service_type FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.id = :oid", {"oid": o_id})
                        
                        client_name = df_single_o.iloc[0]['name'] if not df_single_o.empty else "Client Inconnu"
                        service_type = df_single_o.iloc[0]['service_type'] if not df_single_o.empty else "Type Inconnu"
                        
                        preview_data.append({
                            "Client (Commande)": f"{client_name} - {service_type}",
                            "👨‍✈️ Chauffeur": dict_d.get(a.get("driver_id"), "Non assigné"),
                            "🚚 Camion": dict_v.get(a.get("vehicle_id"), "Non assigné")
                        })
                
                if preview_data:
                    import pandas as pd
                    st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)"""

if target_block in content:
    content = content.replace(target_block, new_block)
    print("Replaced preview logic.")
else:
    print("Preview block not found. Checking if it's slightly different.")

# Remove debug line
content = content.replace('                st.write(st.session_state["ai_proposal"]) # DEBUG\n', '')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
