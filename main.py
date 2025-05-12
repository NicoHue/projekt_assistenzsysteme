from frontend import login
from data.data_storage import DataStorage
import streamlit as st
import atexit


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if "data_storage" not in st.session_state:
        # Hier wird DataStorage nur einmal instanziiert und dann in der Session gespeichert
        st.session_state.data_storage = DataStorage()

    login.render()
    print('Program started')
    # Todo: Löschen der Db am Ende einbauen
    #atexit.register(data_storage.delete_database_on_exit())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
