import re

with open("app.py", "r") as f:
    content = f.read()

old_block = """            today_str = datetime.date.today().strftime('%Y-%m-%d')
            df_assigned = load_data(f\"\"\"
                SELECT v.id as v_id, v.license_plate as v_plate, v.name as v_name,"""

new_block = """            st.write("")
            c_date1, c_date2 = st.columns(2)
            with c_date1:
                jour_select = st.radio("📅 Planning :", ["Aujourd'hui", "Demain"], horizontal=True)
            
            target_date = datetime.date.today()
            if jour_select == "Demain":
                target_date = target_date + datetime.timedelta(days=1)
                
            today_str = target_date.strftime('%Y-%m-%d')
            df_assigned = load_data(f\"\"\"
                SELECT v.id as v_id, v.license_plate as v_plate, v.name as v_name,"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Mobile date picker added.")
else:
    print("Failed to add mobile date picker.")

with open("app.py", "w") as f:
    f.write(content)

