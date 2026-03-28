import re

with open("app.py", "r") as f:
    content = f.read()

content = content.replace(
    "WHERE o.driver_id = {chauffeur_id} AND o.requested_date = '{today_str}'",
    "WHERE o.driver_id = '{chauffeur_id}' AND o.requested_date = '{today_str}'"
)

with open("app.py", "w") as f:
    f.write(content)

