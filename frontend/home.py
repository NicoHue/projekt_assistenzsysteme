import streamlit as st
from frontend import (
    dashboard,
    user_admin,
    customer_admin,
)
from backend.chatbot import chatbot
from data.data_storage import DataStorage
from backend.poseEstimation import main as poseEstimation
import os


def render():
    user = st.session_state["current_user"]
    role = user["role"]
    customer = user["customer"]

    # ================================
    # 🖼️ Kundenlogo anzeigen
    # ================================
    st.sidebar.image(f"backend/data/logos/{customer}.png", use_column_width=True) if customer and os.path.exists(f"backend/data/logos/{customer}.png") else None

    # ================================
    # 🛠 Admin-Tools (nur Master-Admin)
    # ================================
    admin_mode = None
    if role == "master_admin":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠 Admin-Tools")
        admin_mode = st.sidebar.selectbox("Wählen ", [
            "– bitte wählen –",
            "👥 Benutzerverwaltung",
            "🏢 Kundenverwaltung"
        ])

    # ================================
    # 🧭 Modul-Navigation (für alle)
    # ================================
    st.sidebar.title("🏟️ Fußballanalyse")
    mode = st.sidebar.selectbox("Modul wählen", [
        "📊 Dashboard",
        "🎬 Videoanalyse",
        "🤖 Chatbot",
    ], key="main_module")

    # ================================
    # 🔐 Modul-Zugriffsprüfung
    # ================================
    def extract_module_name(mode_entry):
        return mode_entry.split(" ", 1)[1] if " " in mode_entry else mode_entry

    current_module = extract_module_name(mode)
    allowed_modules = user.get("allowed_modules", "all")

    if allowed_modules != "all":
        allowed_list = [m.strip() for m in allowed_modules.split(",")]
        if current_module not in allowed_list:
            st.warning(f"🚫 Kein Zugriff auf das Modul: {current_module}")
            st.stop()

    # ================================
    # 📦 Seite Rendern
    # ================================
    if admin_mode and admin_mode != "– bitte wählen –":
        if admin_mode == "👥 Benutzerverwaltung":
            user_admin.render()
        elif admin_mode == "🏢 Kundenverwaltung":
            customer_admin.render()
    else:
        if mode == "📊 Dashboard":
            dashboard.render()
        elif mode == "🎬 Videoanalyse":
            poseEstimation.render()
        elif mode == "🤖 Chatbot":
            chatbot.render()

    # ================================
    # 👤 Profilbereich
    # ================================
    with st.sidebar.expander("👤 Angemeldet als", expanded=False):
        st.markdown(f"**{user['username']}** ({user['role']})")
        if st.button("🚪 Abmelden"):
            st.session_state["current_user"] = None
            st.rerun()
