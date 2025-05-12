import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# YAML-Datei laden
with open("users.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

    print(config)

# Authenticator erstellen
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Login-Formular anzeigen
name, auth_status, username = authenticator.login(key="Login", location="main")

# Prüfung des Auth-Status
if auth_status:
    st.success(f"✅ Willkommen, {name}!")
    st.session_state["current_user"] = username
    authenticator.logout("Logout", "sidebar")
elif auth_status is False:
    st.error("❌ Falsche Zugangsdaten")
elif auth_status is None:
    st.warning("🔐 Bitte melden Sie sich an.")
