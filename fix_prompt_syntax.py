import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

bad_line = '                            prompt_user = prompt + "\\n\\nStructure exacte exigée pour ton résultat (JSON pur, sans bloc Markdown) :\\n[\\n  {\\"order_id\\": \\"l\'id de la commande\\", \\"driver_id\\": \\"l\'id du chauffeur choisi\\", \\"vehicle_id\\": \\"l\'id du camion choisi\\"}\\n]" order_id\\": 1, \\"driver_id\\": 2, \\"vehicle_id\\": 3} ]"'
good_line = '                            prompt_user = prompt + "\\n\\nStructure exacte exigée pour ton résultat (JSON pur, sans bloc Markdown) :\\n[\\n  {\\"order_id\\": \\"l\'id de la commande\\", \\"driver_id\\": \\"l\'id du chauffeur choisi\\", \\"vehicle_id\\": \\"l\'id du camion choisi\\"}\\n]"'

if bad_line in content:
    content = content.replace(bad_line, good_line)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Syntax fixed.")
else:
    print("Syntax fix not found. Trying regex.")
    
# Try regex
match = re.search(r'prompt_user = prompt.*?\\]" order_id.*?\]"', content)
if match:
    content = content.replace(match.group(0), good_line)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Regex fix applied.")
