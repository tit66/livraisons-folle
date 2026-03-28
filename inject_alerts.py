import re

with open("app.py", "r") as f:
    content = f.read()

# We look for where the dashboard displays the DataFrame df_orders.
old_dash_block = """    if not df_orders.empty:
        df_orders['Date'] = pd.to_datetime(df_orders['Date']).dt.strftime('%d/%m/%Y')
        st.dataframe(df_orders, use_container_width=True, hide_index=True)"""

new_dash_block = """    if not df_orders.empty:
        df_orders['Date'] = pd.to_datetime(df_orders['Date']).dt.strftime('%d/%m/%Y')
        st.dataframe(df_orders, use_container_width=True, hide_index=True)
        
    # ENCART ALERTES
    alerts = check_alerts()
    if alerts:
        st.divider()
        st.warning("### ⚠️ Rappels & Échéances (Chauffeurs & Flotte)")
        for a in alerts:
            st.markdown(f"- {a}")"""

if old_dash_block in content:
    content = content.replace(old_dash_block, new_dash_block)
    with open("app.py", "w") as f:
        f.write(content)
    print("Alerts injected successfully on the dashboard!")
else:
    print("Failed to find dashboard block.")

