import re
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('{"order_id": 1, "driver_id": 2, "vehicle_id": 3}', '{"order_id": "xxx-xxx-xxx", "driver_id": 2, "vehicle_id": 3}')
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
