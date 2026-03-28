import re

with open("app.py", "r") as f:
    content = f.read()

content = content.replace(
    'action_benne = st.radio("Type d\'intervention", ["Pose", "Rotation", "Enlèvement", "Déplacement"], horizontal=True)',
    'action_benne = st.radio("Type d\'intervention", ["Pose", "Rotation", "Enlèvement", "Déplacement sur chantier"], horizontal=True)'
)

with open("app.py", "w") as f:
    f.write(content)
print("Option Déplacement sur chantier added to UI")
