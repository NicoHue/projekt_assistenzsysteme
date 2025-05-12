from datetime import datetime
import streamlit as st
import pandas as pd
import json
from data.data_storage import DataStorage
import matplotlib.pyplot as plt
import plotly.graph_objects as go


# Liste der Mediapipe-Pose-Landmarks (optional erweitert)
LANDMARK_NAMES = [
    "NOSE", "LEFT_EYE_INNER", "LEFT_EYE", "LEFT_EYE_OUTER",
    "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER",
    "LEFT_EAR", "RIGHT_EAR", "MOUTH_LEFT", "MOUTH_RIGHT",
    "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_ELBOW", "RIGHT_ELBOW",
    "LEFT_WRIST", "RIGHT_WRIST", "LEFT_HIP", "RIGHT_HIP",
    "LEFT_KNEE", "RIGHT_KNEE", "LEFT_ANKLE", "RIGHT_ANKLE",
    "LEFT_HEEL", "RIGHT_HEEL", "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX"
]

def render():
    st.header("📊 Dashboard")

    sports = st.session_state.data_storage.get_all_sports()


    # Spieler hinzufügen und speichern
    with st.expander("➕ Neuen Patienten anlegen"):
        with st.form("new_patient_formular",clear_on_submit=True):
            name = st.text_input("Name")
            birthdate = st.date_input("Geburtsdatum", min_value=None, max_value=None)
            birthdate = birthdate.strftime("%d.%m.%Y")

            sport = st.selectbox("Sportart", sports)
            submitted = st.form_submit_button("Patient speichern")
            print("Types:", type(name), type(birthdate), type(sport))
            print("Formatted birthdate:", birthdate)
            if submitted and name and birthdate and sport:
                print(f"\n\n\n{str(name), str(birthdate), str(sport)}\n\n\n")
                st.session_state.data_storage.add_patient({
                    "name": str(name),
                    "birthdate": str(birthdate),
                    "sport": str(sport) if sport else ''
                })
                st.success(f"Patient {name} hinzugefügt.")
                st.rerun()
            elif submitted and name and birthdate and not sport:
                print(f"\n\n\n{str(name), str(birthdate), str(sport)}\n\n\n")
                st.session_state.data_storage.add_patient({
                    "name": str(name),
                    "birthdate": str(birthdate),
                    "sport": None
                })
                st.success(f"Patient {name} hinzugefügt.")
                st.rerun()

    # Patient auswählen
    patients_df = pd.DataFrame(st.session_state.data_storage.get_all_patients())
    if not patients_df.empty:
        patients_df["anzeige"] = patients_df["name"] + " " + patients_df["birthdate"]
        selected_name = st.selectbox("🔽 Patient auswählen", patients_df["anzeige"])
        select_type_of_movement = st.selectbox("Analyseart auswählen", ["Gang", "Lauf", "Sprung"])
        selected_patient = patients_df[patients_df["anzeige"] == selected_name].iloc[0]
        print(f"Patient: {selected_patient} - ID: {selected_patient['id']}")
    else:
        selected_patient = None
        st.info("ℹ️ Noch kein Patient vorhanden.")

    # Patienten-Daten analysieren
    if selected_patient is not None:
        st.subheader(f"📁 Bewegungsdaten von {selected_patient['name']} ({selected_patient['birthdate']})")

        try:
            all_data = st.session_state.data_storage.get_all_movement_data()
            df = pd.DataFrame([entry for entry in all_data if ((int(entry["patient_id"]) == selected_patient["id"]) and (entry["type"] == select_type_of_movement))]) # int-Konvertierung, da "patient_id" in der movement_data als string gespeichert wird

            if df.empty:
                st.warning("Keine Bewegungsdaten für diesen Patienten vorhanden.")
                return

            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            selected_landmark = st.selectbox("📍 Landmark auswählen", LANDMARK_NAMES)
            landmark_index = LANDMARK_NAMES.index(selected_landmark)

            axis_data = {"x": [], "y": [], "z": []}
            timestamps = []

            for _, row in df.iterrows():
                try:
                    landmarks = json.loads(row["landmarks"])
                    point = landmarks[landmark_index]
                    timestamps.append(row["timestamp"])
                    for axis in ["x", "y", "z"]:
                        axis_data[axis].append(point[axis])
                except (json.JSONDecodeError, IndexError, KeyError, TypeError) as e:
                    st.warning(f"Fehler beim Verarbeiten einer Zeile: {e}")

            if timestamps and all(axis_data[axis] for axis in ["x", "y", "z"]):
                col1, col2 = st.columns([2, 1])  # Diagramme links (breiter), Tabelle rechts

                with col1:
                    for axis in ["x", "y", "z"]:
                        st.subheader(f"{selected_landmark} – {axis.upper()}-Achse")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=timestamps,
                            y=axis_data[axis],
                            mode='lines+markers',
                            name=f"{selected_landmark} {axis}",
                            line=dict(width=2),
                            marker=dict(size=5)
                        ))

                        fig.update_layout(
                            xaxis_title="Zeitpunkt",
                            yaxis_title=f"Wert ({axis})",
                            template="plotly_white",
                            height=300,
                            margin=dict(l=40, r=40, t=30, b=30)
                        )

                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("📋 Rohdaten")
                    st.dataframe(df[["timestamp", "landmarks"]], use_container_width=True)

            else:
                st.info("Keine gültigen Landmark-Daten für diesen Patienten.")

        except FileNotFoundError:
            st.error("Die Bewegungsdaten wurden nicht gefunden.")
        except Exception as e:
            st.error("Ein unerwarteter Fehler ist aufgetreten.")
            st.exception(e)

    else:
        st.info("Bitte einen Patienten auswählen.")
