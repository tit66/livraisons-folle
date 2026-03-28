import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Just inject a st.write(st.session_state["ai_proposal"]) right after "Voici la proposition"
target = '                st.success("✅ Voici la proposition de l\'I.A. :")'
replacement = '                st.success("✅ Voici la proposition de l\'I.A. :")\n                st.write(st.session_state["ai_proposal"]) # DEBUG'

if target in content:
    content = content.replace(target, replacement)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Debug injected.")
