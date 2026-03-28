import re

with open("app.py", "r") as f:
    content = f.read()

# Make sure we import folium/streamlit_folium
import_str = """import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import datetime
import os
"""

import_str_new = """import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import datetime
import os
import re as regex
import folium
from streamlit_folium import st_folium
"""

content = content.replace(import_str, import_str_new)


# Function to parse GPS coords from Gmaps link
helper_func = """def est_jour_ouvrable(date_obj):"""
new_helper = """def extract_coords(url):
    try:
        # Format "https://www.google.com/maps/place/42.6976,2.8954" or "@42.6976,2.8954"
        match = regex.search(r'@?([0-9.-]+),([0-9.-]+)', url)
        if match:
            return float(match.group(1)), float(match.group(2))
    except: pass
    return None

def est_jour_ouvrable(date_obj):"""

content = content.replace(helper_func, new_helper)


# Add Map to the details page (Suivi des Bennes)
old_display = """                with st.container():
                    st.markdown(f"#### 🏗️ Chantier : {site_name}")
                    st.markdown(f"**Adresse :** {address}")
                    st.markdown(f"**Volume posé :** 🧰 **{row['net_bennes']} x Benne {row['size']}**")
                    st.markdown(f"[🗺️ Ouvrir dans Google Maps]({gmaps_url})")
                    st.divider()"""

new_display = """                with st.container():
                    st.markdown(f"#### 🏗️ Chantier : {site_name}")
                    st.markdown(f"**Adresse :** {address}")
                    st.markdown(f"**Volume posé :** 🧰 **{row['net_bennes']} x Benne {row['size']}**")
                    st.markdown(f"[🗺️ Ouvrir dans Google Maps]({gmaps_url})")
                    
                    # Carte interactive si on a des coordonnées GPS
                    coords = extract_coords(gmaps_url) if pd.notna(row['gmaps_link']) else None
                    if coords:
                        m = folium.Map(location=[coords[0], coords[1]], zoom_start=15)
                        folium.Marker([coords[0], coords[1]], popup=site_name, tooltip=address, icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
                        st_folium(m, height=250, width=500)
                    else:
                        st.caption("*(Entrez un vrai lien Google Maps avec coordonnées @XX.X,YY.Y dans la fiche client pour afficher la carte interactive ici)*")
                    
                    st.divider()"""

if old_display in content:
    content = content.replace(old_display, new_display)
    with open("app.py", "w") as f:
        f.write(content)
    print("Success map")
else:
    print("Could not find display")

