import streamlit as st
import streamlit_authenticator as stauth
from data.data_storage import DataStorage
from frontend import home


def render():
    st.set_page_config(layout="wide")

    # Initialisiere DataStorage
    data_storage = st.session_state.data_storage

    # Lade Benutzer aus der Datenbank
    users = data_storage.get_all_users()

    # Erstelle das credentials-Dictionary
    credentials = {
        'usernames': {
            user["username"]: {
                'name': user["username"],
                'password': user["password"],  # bcrypt-gehashter Hash
            } for user in users
        }
    }

    # Konfiguriere Cookies und Sessions
    cookie_name = 'streamlit_auth'
    cookie_key = 'some_random_secret_key'  # 🔒 sicher speichern
    expiry_days = 30

    # Erstelle den Authenticator
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        expiry_days
    )
    # Login-Formular anzeigen
    try:
        name, auth_status, username = authenticator.login(location='main', key='Login')
    except TypeError:
        st.error("Login fehlgeschlagen – möglicherweise inkompatible Parameter.")

    if auth_status is False:
        st.error("❌ Falsche Zugangsdaten")

    if auth_status is None:
        st.warning("Bitte melden Sie sich an.")
        st.stop()

    if auth_status:
        st.success(f"✅ Willkommen {name}")
        st.session_state["current_user"] = username
        authenticator.logout("🚪 Logout", "sidebar")
        home.render()
