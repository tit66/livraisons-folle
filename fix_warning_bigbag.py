import re

with open("app.py", "r") as f:
    content = f.read()

old_block = """                if conditionnement == "En vrac":
                    quantite = st.number_input("Quantité (Tonnes)", min_value=0.5, step=0.5, value=1.0)
                    volume_benne = None
                else:
                    quantite = st.number_input("Nombre de Big Bags", min_value=1.0, step=1.0, value=1.0)
                    volume_benne = "Big Bag\""""

new_block = """                if conditionnement == "En vrac":
                    quantite = st.number_input("Quantité (Tonnes)", min_value=0.5, step=0.5, value=1.0)
                    volume_benne = None
                else:
                    st.warning("⚠️ **Avertissement de tarification :** La livraison en Big Bag se fait en camion grue. Il y a une plus-value pour le transport et le conditionnement des matériaux.")
                    quantite = st.number_input("Nombre de Big Bags", min_value=1.0, step=1.0, value=1.0)
                    volume_benne = "Big Bag\""""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Added warning for Big Bags.")
else:
    print("Could not find Big Bag block.")

with open("app.py", "w") as f:
    f.write(content)

