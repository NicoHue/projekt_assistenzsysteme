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

    # Erstelle das credentials-Dictionary --> yaml
    credentials = {
        'usernames': {
            user["username"]: {
                'username': user["username"],
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
    st.write("Credentials Debug:", credentials)

    # Login-Formular anzeigen
    auth_status = None  # Variable vorher definieren
    try:
        result = authenticator.login(location='main', key='Login')

        if result:
            name, auth_status, username = result
            st.write("Debugging:", name, auth_status, username)

        else:
            name, auth_status, username = None, None, None
    except TypeError as e:
        name, auth_status, username = None, None, None
        st.error(f"Login fehlgeschlagen – möglicherweise inkompatible Parameter: {e}")


    except TypeError as e:
        st.error(f"Login fehlgeschlagen – möglicherweise inkompatible Parameter: {e}")

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
