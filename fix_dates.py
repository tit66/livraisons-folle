import re

with open("app.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "format=\"DD/MM/YYYY\"" in line:
        # Just revert the broken lines and do it properly
        line = line.replace(', format="DD/MM/YYYY")', ')')
        line = line.replace(', format="DD/MM/YYYY") else datetime.date.today())', ') else datetime.date.today())')
        lines[i] = line

for i, line in enumerate(lines):
    if "date_caces = st.date_input(" in line: lines[i] = "                date_caces = st.date_input(\"Validité CACES (général)\", format=\"DD/MM/YYYY\")\n"
    elif "chrono_date = st.date_input(" in line: lines[i] = "                chrono_date = st.date_input(\"Date limite Chronotachygraphe (Si applicable)\", format=\"DD/MM/YYYY\")\n"
    elif "limiteur_date = st.date_input(" in line: lines[i] = "                limiteur_date = st.date_input(\"Date limite Limiteur de vitesse (Si applicable)\", format=\"DD/MM/YYYY\")\n"
    elif "new_chrono = st.date_input(" in line: lines[i] = "                new_chrono = st.date_input(\"Fin Chrono\", value=row_v['tachograph_valid_until'] if pd.notna(row_v['tachograph_valid_until']) else datetime.date.today(), format=\"DD/MM/YYYY\")\n"
    elif "new_limiteur = st.date_input(" in line: lines[i] = "                new_limiteur = st.date_input(\"Fin Limiteur\", value=row_v['speed_limiter_valid_until'] if pd.notna(row_v['speed_limiter_valid_until']) else datetime.date.today(), format=\"DD/MM/YYYY\")\n"
    elif "date_permis = st.date_input(" in line: lines[i] = "                date_permis = st.date_input(\"Validité du Permis *\", format=\"DD/MM/YYYY\")\n"
    elif "date_fco = st.date_input(" in line: lines[i] = "                date_fco = st.date_input(\"Validité FIMO / FCO *\", format=\"DD/MM/YYYY\")\n"
    elif "date_carte = st.date_input(" in line: lines[i] = "                date_carte = st.date_input(\"Validité Carte Conducteur *\", format=\"DD/MM/YYYY\")\n"
    elif "new_le = st.date_input(" in line: lines[i] = "                new_le = st.date_input(\"Fin Permis\", value=row['license_expiry'], format=\"DD/MM/YYYY\")\n"
    elif "new_fimo = st.date_input(" in line: lines[i] = "                new_fimo = st.date_input(\"Fin FCO\", value=row['fimo_fco_expiry'], format=\"DD/MM/YYYY\")\n"
    elif "new_carte = st.date_input(" in line: lines[i] = "                new_carte = st.date_input(\"Fin Carte Cond.\", value=row['driver_card_expiry'], format=\"DD/MM/YYYY\")\n"
    elif "ct_date = st.date_input(" in line: lines[i] = "                ct_date = st.date_input(\"Date limite Contrôle Technique *\", format=\"DD/MM/YYYY\")\n"
    elif "new_ct = st.date_input(" in line: lines[i] = "                new_ct = st.date_input(\"Fin CT\", value=row_v['control_valid_until'], format=\"DD/MM/YYYY\")\n"


with open("app.py", "w") as f:
    f.writelines(lines)
