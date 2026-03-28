with open("app.py", "r") as f:
    content = f.read()

new_pages = """
elif navigation == "📍 Suivi des Bennes":
    st.title("📍 Suivi du Parc de Bennes")
    st.write("Où sont nos bennes actuellement ?")
    st.info("Bientôt : Liste des bennes posées chez les clients pour organiser les rotations et enlèvements.")

elif navigation == "📱 Vue Chauffeur (Mobile)":
    st.title("📱 Interface Chauffeur")
    st.write("Vue simplifiée sur smartphone pour les missions du jour.")
    
    chauffeur_connecte = st.selectbox("Se connecter en tant que :", ["Marcel", "Jean", "Paul"])
    st.success(f"👋 Bonjour {chauffeur_connecte} ! Voici tes missions pour aujourd'hui :")
    
    with st.expander("Mission 1 : 08h00 - Livraison Sable", expanded=True):
        st.write("**Client :** Entreprise Martin")
        st.write("**Adresse :** 12 rue de la Paix, Perpignan")
        st.write("**Détails :** 15 Tonnes de Sable")
        st.write("**Instructions :** Code portail 1234")
        st.button("✅ Marquer comme LIVRÉ", key="btn1")
        
    with st.expander("Mission 2 : 10h30 - Rotation Benne", expanded=True):
        st.write("**Client :** Particulier Dupont")
        st.write("**Adresse :** 45 avenue des Fleurs, Cabestany")
        st.write("**Détails :** Rotation Benne 10m3 Gravats")
        st.write("**Instructions :** Attention, petite cour, manœuvrer avec précaution.")
        st.button("✅ Marquer comme TERMINÉ", key="btn2")

"""

content = content.replace('elif navigation == "⚙️ Paramètres":', new_pages + 'elif navigation == "⚙️ Paramètres":')

with open("app.py", "w") as f:
    f.write(content)

