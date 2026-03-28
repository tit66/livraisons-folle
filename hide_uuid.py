import re

with open("app.py", "r") as f:
    content = f.read()

# For Chauffeurs
content = content.replace(
    'st.dataframe(df_d, use_container_width=True, hide_index=True)',
    "st.dataframe(df_d.drop(columns=['ID']), use_container_width=True, hide_index=True)"
)

# For Flotte
content = content.replace(
    'st.dataframe(df_v, use_container_width=True, hide_index=True)',
    "st.dataframe(df_v.drop(columns=['ID']), use_container_width=True, hide_index=True)"
)

with open("app.py", "w") as f:
    f.write(content)

