import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from datetime import datetime
from .utils import calculate_angle
import json

class PoseAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils

    def record_from_webcam(self):
        recording_control = st.session_state.recording_control
        selected_patient = recording_control["selected_patient"]
        analysis_type = recording_control["analysis_type"]

        cap = cv2.VideoCapture(0)
        image_placeholder = st.empty()

        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            st.info("📹 Aufnahme läuft... (zum Beenden bitte Button drücken)")

            while recording_control["running"]:
                ret, frame = cap.read()
                if not ret:
                    st.error("❌ Kamera konnte nicht geöffnet werden.")
                    break

                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_rgb.flags.writeable = False
                results = pose.process(image_rgb)
                image_rgb.flags.writeable = True
                annotated_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                if results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_image,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS
                    )

                    landmarks_data = [
                        {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
                        for lm in results.pose_landmarks.landmark
                    ]

                    data = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "patient_id": int(selected_patient["id"]),
                        "type": analysis_type,
                        "frame": len(recording_control["data"]) + 1,
                        "landmarks": json.dumps(landmarks_data)
                    }

                    recording_control["data"].append(data)

                image_placeholder.image(annotated_image, channels="BGR")

        cap.release()
        st.session_state.recording_control["running"] = False
        st.success("📸 Aufnahme gestoppt.")