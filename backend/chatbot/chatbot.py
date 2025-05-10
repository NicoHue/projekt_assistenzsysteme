import streamlit as st
import requests

def render():
    st.subheader("💬 Chat mit dem Sport-Health-Bot")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Bisherige Nachrichten anzeigen
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Neue Eingabe
    prompt = st.chat_input("Stelle dem Bot eine Frage zu deiner Bewegung...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Anfrage an RASA senden
        response = requests.post(
            "http://localhost:5005/webhooks/rest/webhook",
            json={"sender": "streamlit-user", "message": prompt}
        )

        if response.ok:
            bot_reply = response.json()
            if bot_reply:
                reply_text = bot_reply[0]["text"]
                st.chat_message("assistant").write(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
            else:
                st.chat_message("assistant").write("⚠️ Keine Antwort vom Bot erhalten.")
        else:
            st.chat_message("assistant").write("❌ Fehler bei der Verbindung mit dem Bot.")
