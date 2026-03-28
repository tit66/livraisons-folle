import re

with open("app.py", "r") as f:
    content = f.read()

old_alerts_block = """    alertes_actives = check_alerts()
    if alertes_actives:
        st.error("### 🚨 ALERTES IMPORTANTES (Expiration à < 30 jours)")
        for alert in alertes_actives:
            st.write(alert)
        st.divider()"""

if old_alerts_block in content:
    content = content.replace(old_alerts_block, "")
    with open("app.py", "w") as f:
        f.write(content)
    print("Old alerts removed!")
