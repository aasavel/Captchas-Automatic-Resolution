import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Résolution de Captcha")

url = st.text_input(
    "URL contenant un CAPTCHA",
    "https://solvecaptcha.com/demo/image-captcha"
)

if st.button("Résoudre le CAPTCHA"):
    with st.spinner("Résolution en cours..."):
        r = requests.post(
            f"{API_URL}/captcha/solve-from-url",
            params={"url": url}
        )

        if r.status_code == 200:
            data = r.json()
            st.success("CAPTCHA résolu")
            st.write("Texte détecté :", data["text"])
            st.write("Temps :", data["duration_sec"])
            st.image(data["image_path"])
        else:
            st.error("Erreur API")
