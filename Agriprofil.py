# AgriProfil - Version complète avec GPS réel, date, et textures avancées

import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
from streamlit_js_eval import streamlit_js_eval

# ---------------------- Configuration ----------------------
st.set_page_config(page_title="AgriProfil", layout="wide")
st.title("🌱 AgriProfil - Profil pédologique intelligent")

# ---------------------- Initialisation ----------------------
if 'profil_type' not in st.session_state:
    st.session_state.profil_type = None
if 'layers' not in st.session_state:
    st.session_state.layers = []
if 'photos' not in st.session_state:
    st.session_state.photos = []

# ---------------------- Étape 0 : Type de profil ----------------------
st.sidebar.header("1️⃣ Type de profil")
profil_type = st.sidebar.radio("Comment le profil a-t-il été obtenu ?", 
                               ("🌿 Profil naturel", "🛠️ Profil extrait par tarière"))
st.session_state.profil_type = profil_type
st.markdown(f"### 🔍 Type sélectionné : `{profil_type}`")

# ---------------------- Options avancées ----------------------
st.sidebar.header("🛠️ Options avancées (facultatives)")
activer_gps = st.sidebar.checkbox("📍 Activer GPS réel")
activer_camera = st.sidebar.checkbox("📸 Activer Caméra")

# ---------------------- Données GPS ----------------------
gps_data = None
if activer_gps:
    result = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition((pos) => pos.coords)", 
                               key="get_position")
    if result and isinstance(result, dict) and "latitude" in result:
        gps_data = [result['latitude'], result['longitude']]
        st.sidebar.success(f"📍 Position GPS : {gps_data}")
    else:
        st.sidebar.warning("❗ Impossible d’obtenir la position GPS réelle.")

# ---------------------- Étape 1 : Ajouter une couche ----------------------
st.sidebar.header("2️⃣ Ajouter une couche pédologique")
with st.sidebar.form(key="layer_form"):
    date_profil = st.date_input("📅 Date du profil", value=datetime.now().date())
    heure_profil = st.time_input("⏰ Heure", value=datetime.now().time())

    profondeur_debut = st.number_input("Profondeur début (cm)", min_value=0, step=10)
    profondeur_fin = st.number_input("Profondeur fin (cm)", min_value=0, step=10)
    couleur = st.text_input("Couleur (notation Munsell)")

    texture = st.selectbox("Texture", [
        "sableuse", "limoneuse", "argileuse", "franche",
        "argilo-limoneuse", "limono-argileuse", "sablo-limoneuse",
        "limono-sableuse", "sablo-argileuse", "argilo-sableuse"
    ])
    structure = st.selectbox("Structure", ["massive", "grumeleuse", "prismatique", "platy"])
    carbonates = st.radio("Présence de carbonates (effervescence HCl)", ["Oui", "Non"])
    observations = st.text_area("Autres observations")

    # 📸 Caméra
    photo = None
    if activer_camera:
        photo = st.camera_input("📷 Photo de la couche")

    submit = st.form_submit_button("Ajouter cette couche")

if submit:
    layer = {
        "Date": str(date_profil),
        "Heure": str(heure_profil),
        "Profondeur": f"{profondeur_debut}-{profondeur_fin} cm",
        "Couleur": couleur,
        "Texture": texture,
        "Structure": structure,
        "Carbonates": carbonates,
        "Observations": observations,
        "GPS": gps_data
    }
    st.session_state.layers.append(layer)
    st.session_state.photos.append(photo if photo else None)
    st.success("✅ Couche ajoutée avec succès")

# ---------------------- Étape 2 : Visualisation ----------------------
if st.session_state.layers:
    st.markdown("### 📋 Couches enregistrées")
    df = pd.DataFrame(st.session_state.layers)
    st.dataframe(df, use_container_width=True)

    # Affichage des photos
    for idx, img in enumerate(st.session_state.photos):
        if img:
            st.image(img, caption=f"📷 Photo de la couche {idx+1}", use_column_width=True)

    # ---------------------- Étape 3 : Analyse ----------------------
    st.markdown("### 🤖 Analyse du profil et classification WRB")

    def analyse_profil(layers):
        results = []
        for layer in layers:
            tex = layer['Texture'].lower()
            if "argile" in tex:
                if layer['Carbonates'] == "Oui":
                    results.append("Probable Calcaric Luvisol")
                else:
                    results.append("Probable Dystric Alisol")
            elif "sable" in tex:
                results.append("Probable Arenosol")
            else:
                results.append("Besoin d'analyses supplémentaires")
        return list(set(results))

    wrb_results = analyse_profil(st.session_state.layers)
    for r in wrb_results:
        st.success(f"🔍 WRB suggéré : **{r}**")

    # ---------------------- Étape 4 : Recommandations ----------------------
    st.markdown("### 📌 Recommandations agronomiques")
    for layer in st.session_state.layers:
        if layer['Carbonates'] == "Oui":
            st.warning(f"⛏️ {layer['Profondeur']} : Riche en calcaire, éviter les cultures sensibles.")
        if "argile" in layer['Texture'].lower():
            st.info(f"💧 {layer['Profondeur']} : Favoriser le drainage.")
        if "racine" in layer['Observations'].lower():
            st.success(f"🌱 {layer['Profondeur']} : Présence de racines — bon indicateur de vie du sol.")

    # ---------------------- Étape 5 : Export ----------------------
    st.markdown("### 📤 Exporter les données")
    export_name = f"profil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    st.download_button("📥 Télécharger en CSV", data=df.to_csv(index=False), file_name=export_name, mime="text/csv")
else:
    st.info("Ajoutez au moins une couche pour commencer.")
