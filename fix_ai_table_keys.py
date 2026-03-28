import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix dicts creation to cast keys to string
target_dict_d = "dict_d = {row['id']: f\"{row['first_name']} {row['last_name']}\" for _, row in df_d.iterrows()}"
new_dict_d = "dict_d = {str(row['id']): f\"{row['first_name']} {row['last_name']}\" for _, row in df_d.iterrows()}"

target_dict_v = "dict_v = {row['id']: row['license_plate'] for _, row in df_v.iterrows()}"
new_dict_v = "dict_v = {str(row['id']): row['license_plate'] for _, row in df_v.iterrows()}"

if target_dict_d in content:
    content = content.replace(target_dict_d, new_dict_d)
    content = content.replace(target_dict_v, new_dict_v)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed UUID keys in dicts.")
else:
    print("Target not found.")

