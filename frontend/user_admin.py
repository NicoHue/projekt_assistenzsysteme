import streamlit as st
import logging
from data.data_storage import DataStorage

# Setup Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def render():
    st.title("👥 Benutzerverwaltung")

    current_user = st.session_state.get("current_user")
    if not current_user:
        st.error("Nicht eingeloggt.")
        return

    role = current_user["role"]
    current_customer = current_user["customer"]

    try:
        users = st.session_state.data_storage.get_all_users()
        customers = st.session_state.data_storage.get_all_customers()
    except Exception as e:
        st.error("Fehler beim Laden der Benutzerdaten.")
        logger.error(f"Fehler beim Laden von Nutzern oder Kunden: {e}")
        return

    # ➕ Benutzer anlegen
    st.subheader("➕ Neuen Benutzer anlegen")
    with st.expander("Benutzer hinzufügen"):
        with st.form("create_user_form", clear_on_submit=True):
            new_username = st.text_input("Benutzername")
            new_pw = st.text_input("Passwort", type="password")
            new_role = st.selectbox("Rolle",
                                    ["user", "customer_admin", "master_admin"] if role == "master_admin" else ["user"])
            new_customer = (
                st.selectbox("Kunde", [c["name"] for c in customers])
                if role == "master_admin" else current_customer
            )
            new_allowed = st.multiselect(
                "Zugriffsrechte",
                ["Dashboard", "Mini-Playback", "Taktik-Simulator", "Verletzungsprognose",
                 "Live-Heatmap", "CSV-Export", "Live-Aufnahme", "Chatbot"]
            )

            if st.form_submit_button("➕ Benutzer erstellen"):
                try:
                    st.session_state.data_storage.add_user(
                        new_username,
                        new_role,
                        new_customer,
                        ",".join(new_allowed) if new_allowed else "all",
                        new_pw
                    )
                    st.success(f"Benutzer '{new_username}' wurde erstellt.")
                    logger.info(f"Benutzer '{new_username}' wurde erstellt.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                    logger.warning(f"Fehler beim Erstellen von Benutzer '{new_username}': {e}")
                except Exception as e:
                    st.error("Fehler beim Erstellen des Benutzers.")
                    logger.error(f"Unerwarteter Fehler beim Erstellen von Benutzer '{new_username}': {e}")

    # 🔍 Benutzer filtern
    st.divider()
    st.subheader("🔍 Benutzer filtern")
    search = st.text_input("Suche nach Benutzernamen")
    if role == "master_admin":
        selected_customer = st.selectbox("Nach Kunde filtern", ["Alle"] + [c["name"] for c in customers])
    else:
        selected_customer = current_customer

    # 📋 Benutzerliste
    st.subheader("📋 Benutzerliste")
    filtered_users = [
        u for u in users
        if (search.lower() in u["username"].lower())
        and (selected_customer == "Alle" or u["customer"] == selected_customer)
        and (role == "master_admin" or u["customer"] == current_customer)
    ]

    for u in filtered_users:
        with st.expander(f"👤 {u['username']} ({u['role']}) – {u['customer']}"):
            delete_key = f"delete_mode_{u['username']}"
            if delete_key not in st.session_state:
                st.session_state[delete_key] = False

            # 🔴 Löschbereich (außer aktueller User)
            if u["username"] != current_user["username"]:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if not st.session_state[delete_key]:
                        if st.button("🗑️ Löschen", key=f"del_{u['username']}"):
                            st.session_state[delete_key] = True
                    else:
                        if st.button("❌ Abbrechen", key=f"cancel_{u['username']}"):
                            st.session_state[delete_key] = False
                with col2:
                    if st.session_state[delete_key]:
                        if st.button("⚠️ Löschen bestätigen", key=f"confirm_{u['username']}"):
                            try:
                                st.session_state.data_storage.delete_user(u["username"])
                                st.success(f"Benutzer {u['username']} gelöscht.")
                                logger.info(f"Benutzer {u['username']} gelöscht.")
                                st.session_state.pop(delete_key)
                                st.rerun()
                            except Exception as e:
                                st.error("Fehler beim Löschen des Benutzers.")
                                logger.error(f"Fehler beim Löschen von '{u['username']}': {e}")
                                st.session_state[delete_key] = False

            # ✏️ Bearbeiten
            with st.form(f"edit_{u['username']}"):
                new_role = st.selectbox(
                    "Rolle",
                    ["user", "customer_admin", "master_admin"] if role == "master_admin" else ["user"],
                    index=["user", "customer_admin", "master_admin"].index(u["role"])
                )
                new_allowed = st.multiselect(
                    "Zugriffsrechte",
                    ["Dashboard", "Mini-Playback", "Taktik-Simulator", "Verletzungsprognose",
                     "Live-Heatmap", "CSV-Export", "Live-Aufnahme", "Chatbot"],
                    default=[x.strip() for x in u["allowed_modules"].split(",")] if u["allowed_modules"] != "all" else []
                )
                if st.form_submit_button("💾 Speichern"):
                    try:
                        st.session_state.data_storage.update_user(u["username"], {
                            "role": new_role,
                            "allowed_modules": ",".join(new_allowed) if new_allowed else "all"
                        })
                        st.success("Änderungen gespeichert.")
                        logger.info(f"Benutzer '{u['username']}' aktualisiert.")
                        st.rerun()
                    except Exception as e:
                        st.error("Fehler beim Speichern der Änderungen.")
                        logger.error(f"Fehler beim Aktualisieren von Benutzer '{u['username']}': {e}")
