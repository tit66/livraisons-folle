import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix prompt example format
old_prompt = r'prompt_user = prompt + "\\nFormat JSON exact attendu : [ {\\\"order_id\\\": 1, \\\"driver_id\\\": 2, \\\"vehicle_id\\\": 3} ]"'
new_prompt = r'prompt_user = prompt + "\\nFormat JSON exact attendu : [ {\\\"order_id\\\": \\\"uuid-ou-id\\\", \\\"driver_id\\\": 2, \\\"vehicle_id\\\": 3} ]"'

if old_prompt in content:
    content = content.replace(old_prompt, new_prompt)
    print("Prompt fixed.")

# Fix SQL IN clause for UUIDs
old_ids_line = "ids = ','.join([str(a.get('order_id', 0)) for a in st.session_state['ai_proposal']])"
new_ids_line = "ids = ','.join([f\"'{a.get('order_id', '')}'\" for a in st.session_state['ai_proposal']])"

if old_ids_line in content:
    content = content.replace(old_ids_line, new_ids_line)
    print("IDs query fixed.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
