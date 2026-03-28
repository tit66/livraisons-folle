import re

with open("app.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "df_v = load_data(f\"SELECT id, name, brand, model, license_plate, is_available" in line:
        lines[i] = "            df_v = load_data(f\"SELECT id, name, brand, model, license_plate, is_available, maintenance_notes, control_valid_until, tachograph_valid_until, speed_limiter_valid_until FROM vehicles WHERE type='{t}'\")\n"

with open("app.py", "w") as f:
    f.writelines(lines)
