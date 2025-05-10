import streamlit as st
from data.data_storage import DataStorage
from frontend import home


def render():
    st.set_page_config(layout="wide")

    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None

    if not st.session_state["current_user"]:
        st.title("🔐 Login")
        with st.form("login_form"):
            username = st.text_input("Benutzername")
            password = st.text_input("Passwort", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            user = st.session_state.data_storage.authenticate_user(username, password)
            if user:
                st.session_state["current_user"] = user
                st.rerun()  # 🔁 Seite nach Login neu laden
            else:
                st.error("❌ Falsche Zugangsdaten")
        st.stop()

    # Nach erfolgreichem Login
    home.render()
