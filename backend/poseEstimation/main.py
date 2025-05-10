import streamlit as st
from .pose_analysis import PoseAnalyzer
from data.data_storage import DataStorage
from .visualizations import Visualizations
import pandas as pd


def render():
    st.title("Pose-Analyse Service")

    if "recording_control" not in st.session_state:
        st.session_state.recording_control = {
            "running": False, "data": [], "frames": [],
            "selected_patient": None, "analysis_type": None
        }

    recording_control = st.session_state.recording_control
    visualizations = Visualizations()
    pose_analyzer = PoseAnalyzer()

    # Patientenauswahl
    patients_df = pd.DataFrame(st.session_state.data_storage.get_all_patients())
    if not patients_df.empty:
        patients_df["anzeige"] = patients_df["name"] + " " + patients_df["birthdate"]
        selected_name = st.selectbox("Wählen Sie einen Spieler", patients_df["anzeige"])
        selected_patient = patients_df[patients_df["anzeige"] == selected_name].iloc[0]
        print("DEBUG: selected_patient =", selected_patient)
    else:
        st.info("ℹ️ Noch keine Spieler vorhanden.")
        return

    analysis_type = st.selectbox("Analyseart", ["Gang", "Lauf", "Sprung"])

    # Aufnahme starten
    if not recording_control["running"]:
        if st.button("🎥 Aufnahme starten"):
            st.session_state.recording_control.update({
                "running": True,
                "data": [],
                "frames": [],
                "selected_patient": selected_patient,
                "analysis_type": analysis_type
            })
            pose_analyzer.record_from_webcam()
    else:
        if st.button("🛑 Aufnahme stoppen"):
            st.session_state.recording_control["running"] = False
            if recording_control["data"]:
                st.session_state.data_storage.save_movement_data(recording_control["data"])
                st.success("✅ Daten gespeichert.")
            else:
                st.warning("❌ Keine Daten zum Speichern.")
            st.success("📸 Aufnahme gestoppt.")