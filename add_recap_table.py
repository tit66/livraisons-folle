import re

with open("app.py", "r") as f:
    content = f.read()

old_block = """    c1.metric(label="📦 TOTAL BENNES FLOTTE", value=total_bennes_flotte)
    c2.metric(label="🏗️ BENNES CHEZ LES CLIENTS", value=total_chez_clients)
    c3.metric(label="🏢 BENNES DISPO (DÉPÔT)", value=total_au_depot)"""

new_block = """    c1.metric(label="📦 TOTAL BENNES FLOTTE", value=total_bennes_flotte)
    c2.metric(label="🏗️ BENNES CHEZ LES CLIENTS", value=total_chez_clients)
    c3.metric(label="🏢 BENNES DISPO (DÉPÔT)", value=total_au_depot)
    
    st.divider()
    st.write("### 📊 État du stock détaillé par volume")
    
    df_inv_recap = df_inv.copy()
    if not df_pos.empty:
        df_clients_group = df_pos.groupby('size')['net_bennes'].sum().reset_index()
        df_clients_group.rename(columns={'net_bennes': 'Chez les clients'}, inplace=True)
        df_recap = pd.merge(df_inv_recap, df_clients_group, on='size', how='left')
    else:
        df_recap = df_inv_recap.copy()
        df_recap['Chez les clients'] = 0
        
    df_recap['Chez les clients'] = df_recap['Chez les clients'].fillna(0).astype(int)
    df_recap['Total Flotte'] = df_recap['total_count'].fillna(0).astype(int)
    df_recap['Dispo (Dépôt)'] = df_recap['Total Flotte'] - df_recap['Chez les clients']
    
    df_recap_display = df_recap[['size', 'Total Flotte', 'Chez les clients', 'Dispo (Dépôt)']]
    df_recap_display.columns = ['Volume', 'Total Flotte', 'Chez les clients', 'Dispo (Dépôt)']
    
    st.dataframe(df_recap_display, use_container_width=True, hide_index=True)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("app.py", "w") as f:
        f.write(content)
    print("Recap table added successfully!")
else:
    print("Could not find the metrics block.")
