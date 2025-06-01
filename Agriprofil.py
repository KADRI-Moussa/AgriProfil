# AgriProfil - Application Streamlit pour profil pédologique intelligent (version avec GPS et Caméra uniquement)

import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import geocoder

# ---------------------- Config ----------------------
st.set_page_config(page_title="AgriProfil", layout="wide")
st.title("🌱 AgriProfil - Analyse intelligente de profils pédologiques")

# ---------------------- Initialisation ----------------------
if 'profil_type' not in st.session_state:
    st.session_state.profil_type = None
if 'layers' not in st.session_state:
    st.session_state.layers = []
if 'photos' not in st.session_state:
    st.session_state.photos = []

# ---------------------- Étape 0 : Choix du type de profil ----------------------
st.sidebar.header("1️⃣ Choisissez le type de profil")
profil_type = st.sidebar.radio("Comment le profil a-t-il été obtenu ?", ("🌿 Profil naturel", "🛠️ Profil extrait par tarière"))
st.session_state.profil_type = profil_type
st.markdown(f"### 🔍 Type sélectionné : `{profil_type}`")

# ---------------------- Options avancées ----------------------
st.sidebar.header("🛠️ Options avancées (facultatives)")
activer_gps = st.sidebar.checkbox("📍 Activer GPS")
activer_camera = st.sidebar.checkbox("📸 Activer Caméra")

# ---------------------- Données GPS ----------------------
gps_data = None
if activer_gps:
    g = geocoder.ip('me')
    gps_data = g.latlng
    if gps_data:
        st.sidebar.success(f"📍 Position GPS : {gps_data}")
    else:
        st.sidebar.warning("❗ Impossible de récupérer le GPS")

# ---------------------- Étape 1 : Formulaire d'ajout de couche ----------------------
st.sidebar.header("2️⃣ Ajoutez une couche pédologique")
with st.sidebar.form(key="layer_form"):
    profondeur_debut = st.number_input("Profondeur début (cm)", min_value=0, step=10)
    profondeur_fin = st.number_input("Profondeur fin (cm)", min_value=0, step=10)
    couleur = st.text_input("Couleur (notation Munsell)")
    texture = st.selectbox("Texture", ["sableuse", "limoneuse", "argileuse", "franche"])
    structure = st.selectbox("Structure", ["massive", "grumeleuse", "prismatique", "platy"])
    carbonates = st.radio("Présence de carbonates (effervescence HCl)", ["Oui", "Non"])
    observations = st.text_area("Autres observations")

    # 📸 Caméra
    photo = None
    if activer_camera:
        photo = st.camera_input("📷 Prenez une photo de la couche")

    submit = st.form_submit_button("Ajouter cette couche")

if submit:
    layer = {
        "Profondeur": f"{profondeur_debut}-{profondeur_fin} cm",
        "Couleur": couleur,
        "Texture": texture,
        "Structure": structure,
        "Carbonates": carbonates,
        "Observations": observations,
        "GPS": gps_data
    }
    st.session_state.layers.append(layer)
    if photo:
        st.session_state.photos.append(photo)
    else:
        st.session_state.photos.append(None)
    st.success("✅ Couche ajoutée avec succès")

# ---------------------- Étape 2 : Visualisation ----------------------
if st.session_state.layers:
    st.markdown("### 📋 Couches enregistrées")
    df = pd.DataFrame(st.session_state.layers)
    st.dataframe(df, use_container_width=True)

    # Afficher les photos
    for idx, img in enumerate(st.session_state.photos):
        if img:
            st.image(img, caption=f"📷 Photo de la couche {idx+1}", use_column_width=True)

    # ---------------------- Étape 3 : Analyse intelligente ----------------------
    st.markdown("### 🤖 Analyse du profil et classification WRB")

    def analyse_profil(layers):
        results = []
        for layer in layers:
            if "argileuse" in layer['Texture'].lower():
                if layer['Carbonates'] == "Oui":
                    results.append("Probable Calcaric Luvisol")
                else:
                    results.append("Probable Dystric Alisol")
            elif "sableuse" in layer['Texture'].lower():
                results.append("Probable Arenosol")
            else:
                results.append("Besoin d'analyses supplémentaires")
        return list(set(results))

    wrb_results = analyse_profil(st.session_state.layers)
    for r in wrb_results:
        st.success(f"🔍 Classification WRB suggérée : **{r}**")

    # ---------------------- Étape 4 : Recommandations ----------------------
    st.markdown("### 📌 Recommandations agronomiques")
    for layer in st.session_state.layers:
        if layer['Carbonates'] == "Oui":
            st.warning(f"⛏️ Couche {layer['Profondeur']} : Riche en calcaire, éviter les cultures sensibles.")
        if layer['Texture'] == "argileuse":
            st.info(f"💧 Couche {layer['Profondeur']} : Favoriser le drainage pour éviter l'engorgement.")
        if "racine" in layer['Observations'].lower():
            st.success(f"🌱 Couche {layer['Profondeur']} : Présence de racines — bon indicateur de vie du sol.")

    # ---------------------- Étape 5 : Export ----------------------
    st.markdown("### 📤 Exporter les données")
    export_name = f"profil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    st.download_button("📥 Télécharger le tableau en CSV", data=df.to_csv(index=False), file_name=export_name, mime="text/csv")
else:
    st.info("Ajoutez au moins une couche pour lancer l'analyse.")
