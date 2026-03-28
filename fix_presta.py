import re

with open("app.py", "r") as f:
    content = f.read()

content = content.replace(
    'prestation = st.radio("3️⃣ Type de Prestation", ["Livraison de matériaux", "Location de benne", "Autre"], horizontal=True)',
    'prestation = st.radio("3️⃣ Type de Prestation", ["Livraison de matériaux", "Location de benne"], horizontal=True)'
)

# And make sure any code relying on "Autre" doesn't break
# "Autre" logic was just skipping everything anyway, so no harm in removing it.

with open("app.py", "w") as f:
    f.write(content)
print("Removed 'Autre' from prestation.")
