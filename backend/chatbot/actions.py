from typing import Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Hier ggf. dein eigenes Modul importieren
from data.data_storage import DataStorage



class action_request_movement_data(Action):
    def name(self) -> str:
        return "action_request_movement_data"

    def __init__(self):
        self.data_storage = DataStorage()

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[str, Any]) -> List[Dict[str, Any]]:

        name = tracker.get_slot("name")
        birthdate = tracker.get_slot("birthdate")

        if not name:
            dispatcher.utter_message(response="utter_ask_name")
            return []

        matching_patients = self.data_storage.get_patient_by_name(name)

        if not matching_patients:
            dispatcher.utter_message(response="utter_no_patient_found")
            return []

        # Wenn nur ein Patient mit diesem Namen
        if len(matching_patients) == 1:
            patient = matching_patients[0]
        else:
            # Geburtstdatum notwendig
            if not birthdate:
                options = ", ".join([f"{p['name']} ({p['birthdate']})" for p in matching_patients])
                dispatcher.utter_message(text=f"⚠️ Es gibt mehrere Patienten mit diesem Namen. Bitte gib das Geburtsdatum an: {options}")
                return []

            patient = next((p for p in matching_patients if p["birthdate"] == birthdate), None)
            if not patient:
                dispatcher.utter_message(response="utter_no_patient_found")
                return []

        movement_data = self.data_storage.get_movement_data_of_patient(patient["id"])

        dispatcher.utter_message(response="utter_display_data", name=patient["name"], id=patient["id"], data=movement_data)
        return [SlotSet("patient_id", patient["id"])]
