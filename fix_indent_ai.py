import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

bad_indent = """    import datetime as dt
        date_planning = st.date_input("Date du planning à préparer", dt.date.today() + dt.timedelta(days=1))"""

good_indent = """    import datetime as dt
    date_planning = st.date_input("Date du planning à préparer", dt.date.today() + dt.timedelta(days=1))"""

if bad_indent in content:
    content = content.replace(bad_indent, good_indent)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed.")
else:
    print("Not found.")
