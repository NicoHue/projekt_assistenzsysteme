from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import streamlit as st

class ActionShowPlayerData(Action):
    def name(self):
        return "action_show_player_data"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.get_slot("spieler_id")  # gesetzt beim Login
        is_admin = tracker.get_slot("is_admin")   # true/false

        df = st.session_state.data_storage.get_all_movement_data

        if is_admin:
            result = df.head(5)  # z.B. erste 5 Einträge aller Spieler
            dispatcher.utter_message(text=f"Hier sind die letzten Daten:\n{result}")
        elif user_id:
            player_data = df[df["spieler_id"] == user_id]
            dispatcher.utter_message(text=f"Hier sind deine letzten Daten:\n{player_data.head(5)}")
        else:
            dispatcher.utter_message(response="utter_no_permission")

        return []
