import streamlit as st
import logging
from PIL import Image
from io import BytesIO
from data.data_storage import DataStorage

# Setup Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MAX_IMAGE_WIDTH = 800  # Maximale Breite des Logos
MAX_IMAGE_HEIGHT = 800  # Maximale Höhe des Logos


def resize_image(image: Image.Image) -> Image.Image:
    """Skaliert das Bild, wenn es zu groß ist."""
    width, height = image.size
    ratio = min(MAX_IMAGE_WIDTH / width, MAX_IMAGE_HEIGHT / height)
    if ratio < 1:
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size, Image.ANTIALIAS)
    return image


def render():
    st.title("🏢 Kundenverwaltung")

    current_user = st.session_state.get("current_user")
    if not current_user:
        st.error("Nicht eingeloggt.")
        return

    if current_user["role"] != "master_admin":
        st.error("Nur der Master-Admin kann Kunden verwalten.")
        return

    try:
        customers = st.session_state.data_storage.get_all_customers()
        sports = st.session_state.data_storage.get_all_sports()
    except Exception as e:
        st.error("Fehler beim Laden der Kundendaten.")
        logger.error(f"Fehler beim Laden der Kunden oder Sportarten: {e}")
        return

    # ➕ Neuer Kunde
    st.subheader("➕ Neuen Kunden anlegen")
    with st.expander("Kunden hinzufügen"):
        with st.form("create_customer_form"):
            new_name = st.text_input("Kundenname")
            new_description = st.text_area("Beschreibung")
            new_logo = st.file_uploader("Logo hochladen", type=["png", "jpg", "jpeg"])

            if new_logo:
                image = Image.open(new_logo)
                resized_image = resize_image(image)
                st.image(resized_image, use_column_width=True)

            if st.form_submit_button("➕ Kunden anlegen"):
                try:
                    logo_path = None
                    if new_logo:
                        # Umwandeln in Bytes für Speicherung
                        buffered = BytesIO()
                        resized_image.save(buffered, format="PNG")
                        logo_path = st.session_state.data_storage.save_logo(new_name, buffered.getvalue())

                    st.session_state.data_storage.add_customer(new_name, new_description, logo_path)
                    logger.info(f"Kunde '{new_name}' erfolgreich angelegt.")
                    st.success(f"Kunde '{new_name}' wurde erfolgreich angelegt.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler beim Anlegen des Kunden.")
                    logger.error(f"Fehler beim Anlegen von Kunde '{new_name}': {e}")

    # 🔍 Kunden filtern
    # todo: Weitere Filtermöglichkeit einbauen
    st.divider()
    st.subheader("🔍 Kunden suchen")
    search = st.text_input("Kundennamen eingeben")
    filtered_customers = [c for c in customers if search.lower() in c["name"].lower()]

    # 📋 Kundenliste
    st.subheader("📋 Kundenliste")
    for customer in filtered_customers:
        with st.expander(f"🏢 {customer['name']}"):
            delete_key = f"delete_mode_{customer['name']}"
            if delete_key not in st.session_state:
                st.session_state[delete_key] = False

            col1, col2 = st.columns([1, 2])
            with col1:
                if not st.session_state[delete_key]:
                    if st.button("🗑️ Löschen", key=f"del_{customer['name']}"):
                        st.session_state[delete_key] = True
                else:
                    if st.button("❌ Abbrechen", key=f"cancel_{customer['name']}"):
                        st.session_state[delete_key] = False

            with col2:
                if st.session_state[delete_key]:
                    if st.button("⚠️ Löschen bestätigen", key=f"confirm_{customer['name']}"):
                        try:
                            st.session_state.data_storage.delete_customer(customer["name"])
                            logger.info(f"Kunde '{customer['name']}' gelöscht.")
                            st.success(f"Kunde '{customer['name']}' gelöscht.")
                            st.session_state.pop(delete_key)
                            st.rerun()
                        except Exception as e:
                            st.error("Fehler beim Löschen.")
                            logger.error(f"Fehler beim Löschen von Kunde '{customer['name']}': {e}")
                            st.session_state[delete_key] = False

            # ✏️ Bearbeiten
            with st.form(f"edit_{customer['name']}"):
                new_name = st.text_input("Name", value=customer["name"])
                new_description = st.text_area("Beschreibung", value=customer.get("description", ""))
                new_logo = st.file_uploader("Logo ersetzen (optional)", type=["png", "jpg", "jpeg"])

                if new_logo:
                    image = Image.open(new_logo)
                    resized_image = resize_image(image)
                    st.image(resized_image, use_column_width=True)

                if st.form_submit_button("💾 Änderungen speichern"):
                    try:
                        logo_path = None
                        if new_logo:
                            # Umwandeln in Bytes für Speicherung
                            buffered = BytesIO()
                            resized_image.save(buffered, format="PNG")
                            logo_path = st.session_state.data_storage.save_logo(new_name, buffered.getvalue())

                        st.session_state.data_storage.update_customer(
                            customer["name"],
                            {
                                "name": new_name,
                                "description": new_description,
                                "logo_path": logo_path or customer.get("logo_path", "")
                            }
                        )
                        logger.info(f"Kunde '{customer['name']}' aktualisiert.")
                        st.success(f"Kunde '{new_name}' wurde aktualisiert.")
                        st.rerun()
                    except Exception as e:
                        st.error("Fehler beim Speichern der Änderungen.")
                        logger.error(f"Fehler beim Aktualisieren von Kunde '{customer['name']}': {e}")

