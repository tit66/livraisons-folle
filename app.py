import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Livraisons Folles - Dispatch",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONNALISÉ (Surtout pour les boutons "Chauffeur") ---
st.markdown("""
<style>
/* Gros boutons d'action (pour les gros doigts sur smartphone) */
div.stButton > button {
    height: 60px;
    font-size: 1.2rem;
    font-weight: bold;
    border-radius: 8px;
    border: 2px solid #E65100;
}
/* Style "Danger" pour les problèmes */
.btn-danger {
    background-color: #DC3545 !important;
    color: white !important;
    border: none !important;
}
/* Style "Succès" pour les livraisons */
.btn-success {
    background-color: #28A745 !important;
    color: white !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Navigation principale) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/150/000000/dump-truck.png", width=100) # Un petit logo de camion/benne
    st.title("Livraisons Folles")
    st.markdown("---")
    vue = st.radio(
        "Sélectionnez votre vue :",
        ["🖥️ Dispatch (Bureau)", "📱 Chauffeur (Mobile)", "⚙️ Paramètres"]
    )
    st.markdown("---")
    st.write("Connecté en tant que: **Thierry** 👷‍♂️")

# --- VUE DISPATCH (Bureau) ---
if vue == "🖥️ Dispatch (Bureau)":
    st.header("🖥️ Tour de Contrôle / Planning")
    st.caption("Vue globale pour l'affectation et le suivi des bennes.")
    
    # 1. METRICS (Gros compteurs en haut)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🗑️ Bennes Déposées", "12", "En cours")
    col2.metric("🚚 Camions sur route", "3", "Tournées en cours")
    col3.metric("⏳ Retards ou Urgences", "1", "-1h (Alerte)", delta_color="inverse")
    col4.metric("📞 Appels en attente", "2")
    
    st.markdown("---")
    
    # 2. PLANNING (Faux tableau pour la démo)
    st.subheader("Planning du jour (Bennes 8m³, 10m³, 15m³)")
    # (À l'avenir on utilisera st_aggrid pour un vrai tableau interactif)
    st.dataframe(
        {
            "Client": ["Chantier Dupont", "Mairie (Espaces Verts)", "Particulier Martin", "BTP Construction"],
            "Type Benne": ["Gravats 10m³", "DIB 15m³", "Bois 8m³", "Gravats 10m³"],
            "Action Prévue": ["Dépose (Matin)", "Rotation", "Retrait (Soir)", "Dépose (Matin)"],
            "Chauffeur": ["Jean 🚚", "Michel 🚛", "Jean 🚚", "⚠️ Non assigné"],
            "Statut": ["En route 🟢", "Sur site 🟡", "Attente ⚪", "À planifier 🔴"]
        },
        use_container_width=True
    )

# --- VUE CHAUFFEUR (Mobile) ---
elif vue == "📱 Chauffeur (Mobile)":
    st.header("📱 Ma Tournée du Jour")
    st.info("Chauffeur : Jean | Camion : 🚛 Immat. AB-123-CD")
    
    # Carte de mission 1
    with st.expander("🗑️ 08:30 - Chantier Dupont (Dépose 10m³ Gravats)", expanded=True):
        st.write("**Adresse:** 12 Rue des Oliviers, 66000 Perpignan")
        st.write("**Contact:** M. Dupont (06 12 34 56 78)")
        st.write("**Instructions:** Attention au portail électrique, se garer en marche arrière.")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ LIVRÉ", key="btn_livre1", help="Confirmer la pose de la benne"):
                st.success("Benne déposée et confirmée ! 🗑️")
        with col_btn2:
            if st.button("⚠️ PROBLÈME", key="btn_prob1"):
                st.error("Problème signalé au Dispatch ! 📞")
                
    # Carte de mission 2
    with st.expander("♻️ 11:00 - Mairie (Rotation 15m³ DIB)", expanded=False):
        st.write("**Adresse:** Parc des Sports, 66000 Perpignan")
        st.write("**Instructions:** Entrée par l'arrière du gymnase.")
        st.button("✅ ROTATION FAITE", key="btn_rot2")

# --- VUE PARAMÈTRES ---
else:
    st.header("⚙️ Configuration Système")
    st.write("Ici on gérera :")
    st.markdown("- La flotte de camions 🚛")
    st.markdown("- L'inventaire des bennes (avec QR Codes) 🗑️")
    st.markdown("- La configuration de l'IA de planning 🧠")
