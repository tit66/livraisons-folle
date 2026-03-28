import re

with open("app.py", "r") as f:
    content = f.read()

# Update the SQL logic in Suivi des Bennes to correctly account for the exact strings
# Pose -> +1
# Rotation -> 0 (it replaces a full with an empty, so net amount of skips on site is still 1)
# Enlèvement -> -1
# Déplacement sur chantier -> 0 (just moves the skip, net amount on site is 1 still)

# The current query:
# SUM(CASE WHEN o.service_type = 'Benne - Pose' THEN 1 WHEN o.service_type = 'Benne - Enlèvement' THEN -1 ELSE 0 END) as net_bennes

old_query_pos = """    query_pos = \"\"\"
        SELECT c.id as client_id, c.name as client_name, s.label as site_label, 
               COALESCE(s.address, c.billing_address) as address, 
               s.gmaps_link as gmaps_link, o.container_type as size, 
               SUM(CASE WHEN o.service_type = 'Benne - Pose' THEN 1 
                        WHEN o.service_type = 'Benne - Enlèvement' THEN -1 
                        ELSE 0 END) as net_bennes
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        LEFT JOIN sites s ON o.site_id = s.id
        WHERE o.service_type LIKE 'Benne %'
        GROUP BY c.id, c.name, s.label, COALESCE(s.address, c.billing_address), s.gmaps_link, o.container_type
        HAVING SUM(CASE WHEN o.service_type = 'Benne - Pose' THEN 1 WHEN o.service_type = 'Benne - Enlèvement' THEN -1 ELSE 0 END) > 0
    \"\"\""""

new_query_pos = """    query_pos = \"\"\"
        SELECT c.id as client_id, c.name as client_name, s.label as site_label, 
               COALESCE(s.address, c.billing_address) as address, 
               s.gmaps_link as gmaps_link, o.container_type as size, 
               SUM(CASE WHEN o.service_type = 'Benne - Pose' AND o.status = 'done' THEN 1 
                        WHEN o.service_type = 'Benne - Enlèvement' AND o.status = 'done' THEN -1 
                        ELSE 0 END) as net_bennes
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        LEFT JOIN sites s ON o.site_id = s.id
        WHERE o.service_type LIKE 'Benne %'
        GROUP BY c.id, c.name, s.label, COALESCE(s.address, c.billing_address), s.gmaps_link, o.container_type
        HAVING SUM(CASE WHEN o.service_type = 'Benne - Pose' AND o.status = 'done' THEN 1 WHEN o.service_type = 'Benne - Enlèvement' AND o.status = 'done' THEN -1 ELSE 0 END) > 0
    \"\"\""""

# Let's verify the query logic.
# Wait, "Déplacement sur chantier" and "Rotation" don't add or subtract to the total count of skips AT THAT SPECIFIC CLIENT.
# But what if a client orders a rotation without having ordered a pose first? The system assumes they had one.
# That's fine for this MVP.
# Also we must make sure the query relies on `status = 'done'`, otherwise pending orders change the inventory!

if old_query_pos in content:
    content = content.replace(old_query_pos, new_query_pos)
    with open("app.py", "w") as f:
        f.write(content)
    print("Fixed tracking query!")
else:
    print("Could not find tracking query!")

