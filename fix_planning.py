import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Update planning query for vehicles (they don't have is_active, they have is_available)
old_veh_query = 'df_vehicules = load_data("SELECT id, license_plate, brand_model, vehicle_type FROM vehicles WHERE is_active = true ORDER BY vehicle_type")'
new_veh_query = 'df_vehicules = load_data("SELECT id, license_plate, type as vehicle_type, name as brand_model FROM vehicles WHERE is_available = true ORDER BY type")'

if old_veh_query in content:
    content = content.replace(old_veh_query, new_veh_query)
    print("Fixed vehicle query in planning")
else:
    print("Failed to find vehicle query in planning")

with open("app.py", "w") as f:
    f.write(content)

