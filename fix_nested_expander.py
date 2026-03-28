import re

with open("app.py", "r") as f:
    content = f.read()

old_block = """                            with st.expander("❌ Signaler un problème"):
                                with st.form(f"form_issue_mission_{m['id']}"):"""

new_block = """                            if st.checkbox("❌ Signaler un problème", key=f"chk_issue_mission_{m['id']}"):
                                with st.form(f"form_issue_mission_{m['id']}"):"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Nested expander fixed using checkbox.")
else:
    print("Could not find nested expander.")

with open("app.py", "w") as f:
    f.write(content)

