import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Update the insert logic when creating an order to match the "Type d'intervention" string format.
# Prestation string in DB right now: "Benne - Pose", "Benne - Enlèvement", etc.
# Wait, let's check how the insert query looks in Prise de Commande.
