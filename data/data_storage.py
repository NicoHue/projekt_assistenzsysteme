import sqlite3
import os
import logging
from datetime import datetime
import hashlib
import streamlit as st

# todo: Logging in das main.py verlagern

# Logging konfigurieren
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "app.log"),
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("[%(levelname)s] %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)


# todo: Prüfen, warum immer wieder ein DataStorage initialisiert wird, wenn ein Datenzugriff gemacht wurde
class DataStorage:

    # --- class init ---

    def __init__(self):
        try:
            self.base_dir = os.getcwd()
            self.db_path = os.path.join(self.base_dir, "data\database.db")
            self.video_path = os.path.join(self.base_dir, "videos")
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
            self.ensure_video_folder_exists()

            if not self.get_customer_by_name('Owner'):
                self.add_customer('Owner', 'Owner')
                self.add_user('admin', 'master_admin', 'Owner', 'all', 'admin123')

            if not self.get_patient_by_name('Max Mustermann'):
                self.add_patient('Max Mustermann', '01.01.2000')

            logging.info("✅ DataStorage initialisiert.")
            logging.debug(f"base_dir = {self.base_dir}")
            logging.debug(f"db_path = {self.db_path}")
        except Exception as e:
            logging.exception(f"❌ Fehler bei Initialisierung: {e}")

    # --- folder path ---

    def ensure_video_folder_exists(self):
        try:
            os.makedirs(self.video_path, exist_ok=True)
        except Exception as e:
            logging.error(f"❌ Fehler beim Erstellen des Video-Ordners: {e}")

    # --- data base ---

    def connect(self):
        try:
            if not hasattr(self, 'conn') or self.conn is None:
                self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
                self._create_tables()
            return self.conn
        except Exception as e:
            logging.exception("❌ Fehler beim Verbinden mit der Datenbank")

    def delete_database_on_exit(self):
        try:
            self.conn.close()
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                logging.info("🗑️ Datenbank wurde beim Beenden gelöscht.")
            else:
                logging.warning("⚠️ Keine Datenbank gefunden zum Löschen.")
        except Exception as e:
            logging.exception("❌ Fehler beim Löschen der Datenbank")

    def _create_tables(self):
        try:
            with self.conn:
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        user TEXT NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL,
                        customer TEXT,
                        allowed_modules TEXT DEFAULT 'all'
                    );
                ''')
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT
                    );
                ''')
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS movement_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        patient_id TEXT,
                        type TEXT,
                        frame INTEGER,
                        landmarks TEXT
                    );
                ''')
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS sports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sport TEXT UNIQUE NOT NULL
                    );
                ''')
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        birthdate TEXT,
                        sport TEXT
                    );
                ''')
        except Exception as e:
            logging.exception("❌ Fehler beim Erstellen der Tabellen")

    # --- movement_data ---

    def save_movement_data(self, data_list):
        try:
            with self.conn:
                self.conn.executemany('''
                    INSERT INTO movement_data (timestamp, patient_id, type, frame, landmarks)
                    VALUES (?, ?, ?, ?, ?)
                ''', [
                    (
                        entry.get("timestamp", datetime.now().isoformat()),
                        entry["patient_id"],
                        entry["type"],
                        entry["frame"],
                        entry["landmarks"]
                    ) for entry in data_list
                ])
            logging.info("✅ Bewegungsdaten gespeichert.")
        except Exception as e:
            logging.exception("❌ Fehler beim Speichern von Bewegungsdaten")

    def get_all_movement_data(self):
        try:
            cursor = self.conn.execute('SELECT * FROM movement_data')
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.exception("❌ Fehler beim Laden von Bewegungsdaten")
            return []

    def get_movement_data_of_patient(self, patient=st.session_state["current_user"]):
        try:
            cursor = self.conn.execute('SELECT * FROM movement_data WHERE patient_id = ?', (patient,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.exception("❌ Fehler beim Laden von Bewegungsdaten")
            return []

    # --- sports ---

    def get_all_sports(self):
        try:
            cursor = self.conn.execute('SELECT sport FROM sports')
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.exception("❌ Fehler beim Abrufen der Sportarten")
            return []

    def add_sport(self, sport):
        try:
            with self.conn:
                self.conn.execute('INSERT OR IGNORE INTO sports (sport) VALUES (?)', (sport,))
        except Exception as e:
            logging.exception("❌ Fehler beim Hinzufügen der Sportart")

    # --- patient ---

    def add_patient(self, name, birthdate=None, sport=None):
        print(f"\n\n\n{name, birthdate, sport}\n\n\n")
        try:
            with self.conn:
                self.conn.execute('INSERT INTO patients (name, birthdate, sport) VALUES (?, ?, ?)',
                                  (str(name), str(birthdate), str(sport),))
        except Exception as e:
            logging.exception("❌ Fehler beim Hinzufügen eines Patienten")

    def get_patient_by_name_and_birthdate(self, name: str, birth_date: str) -> dict:
        # Gibt z.B. {"id": 3, "name": "Max Mustermann", "birth_date": "1990-01-01", "data": "..."} zurück
        try:
            self.connect()
            cursor = self.conn.execute("SELECT * FROM patients WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logging.exception("❌ Fehler beim Abrufen des Patienten")
            return None

    def get_patient_by_name(self, patient):
        try:
            self.connect()
            cursor = self.conn.execute("SELECT * FROM patients WHERE name = ?", (patient,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logging.exception("❌ Fehler beim Abrufen des Patienten")
            return None

    def get_all_patients(self):
        try:
            cursor = self.conn.execute('SELECT * FROM patients')
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.exception("❌ Fehler beim Laden der Patienten")
            return []

    def delete_patient(self, patient_id):
        try:
            with self.conn:
                self.conn.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
                logging.info(f"🗑️ Patient mit ID {patient_id} gelöscht.")
        except Exception as e:
            logging.exception("❌ Fehler beim Löschen des Patienten")

    # --- user ---

    def add_user(self, username, role, customer, allowed_modules, password):
        try:
            self.connect()
            if self.get_user_by_name(username):
                raise ValueError(f"Nutzer '{username}' existiert bereits.")
            hashed_pw = self.hash_password(password)
            with self.conn:
                self.conn.execute("""
                    INSERT INTO users (username, user, password, role, customer, allowed_modules)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, username, hashed_pw, role, customer, allowed_modules))
        except Exception as e:
            logging.exception("❌ Fehler beim Hinzufügen eines Nutzers")

    def delete_user(self, username):
        try:
            self.connect()
            with self.conn:
                self.conn.execute("DELETE FROM users WHERE username = ?", (username,))
                logging.info(f"🗑️ Nutzer '{username}' gelöscht.")
        except Exception as e:
            logging.exception("❌ Fehler beim Löschen des Nutzers")

    def update_user(self, old_name, updated_fields):
        try:
            self.connect()
            fields = []
            values = []
            for key, value in updated_fields.items():
                fields.append(f"{key} = ?")
                values.append(value)
            values.append(old_name)
            query = f"UPDATE users SET {', '.join(fields)} WHERE username = ?"
            with self.conn:
                self.conn.execute(query, tuple(values))
        except Exception as e:
            logging.exception("❌ Fehler beim Aktualisieren des Nutzers")

    def get_all_users(self):
        try:
            self.connect()
            cursor = self.conn.execute("SELECT * FROM users")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.exception("❌ Fehler beim Abrufen der Nutzer")
            return []

    def get_user_by_name(self, username):
        try:
            self.connect()
            cursor = self.conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logging.exception("❌ Fehler beim Abrufen des Nutzers")
            return None

    def authenticate_user(self, username, password):
        try:
            users = self.get_all_users()
            for user in users:
                if user["username"] == username and self.check_password(password, user.get("password", "")):
                    return user
            return None
        except Exception as e:
            logging.exception("❌ Fehler bei der Authentifizierung")
            return None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, input_password, stored_hash):
        return self.hash_password(input_password) == stored_hash

    # --- customer ---

    def get_all_customers(self):
        try:
            self.connect()
            result = self.conn.execute("SELECT * FROM customers").fetchall()
            return [dict(row) for row in result]
        except Exception as e:
            logging.exception("❌ Fehler beim Abrufen der Kunden")
            return []

    def get_customer_by_name(self, name):
        try:
            self.connect()
            row = self.conn.execute("SELECT * FROM customers WHERE name = ?", (name,)).fetchone()
            return dict(row) if row else None
        except Exception as e:
            logging.exception("❌ Fehler beim Abrufen des Kunden")
            return None

    def add_customer(self, name, description, logo_path=None):
        try:
            self.connect()
            if self.get_customer_by_name(name):
                raise ValueError(f"Kunde '{name}' existiert bereits.")
            with self.conn:
                self.conn.execute("INSERT INTO customers (name, description) VALUES (?, ?)", (name, description))
            self.add_user(f"admin_{name}", "customer_admin", name, "all", "Admin123")
        except Exception as e:
            logging.exception("❌ Fehler beim Hinzufügen eines Kunden")

    def update_customer(self, old_name, updated_fields):
        try:
            self.connect()
            fields = []
            values = []
            for key, value in updated_fields.items():
                fields.append(f"{key} = ?")
                values.append(value)
            values.append(old_name)
            query = f"UPDATE customers SET {', '.join(fields)} WHERE name = ?"
            with self.conn:
                self.conn.execute(query, tuple(values))
        except Exception as e:
            logging.exception("❌ Fehler beim Aktualisieren des Kunden")

    def delete_customer(self, name):
        try:
            self.connect()
            with self.conn:
                self.conn.execute("DELETE FROM users WHERE customer = ?", (name,))
                self.conn.execute("DELETE FROM customers WHERE name = ?", (name,))
                logging.info(f"🗑️ Kunde '{name}' gelöscht.")
        except Exception as e:
            logging.exception("❌ Fehler beim Löschen des Kunden")

    # --- logo ---

    def save_logo(self, customer_name, image_bytes):
        try:
            logo_dir = os.path.join(self.base_dir, "data", "logos")
            os.makedirs(logo_dir, exist_ok=True)
            logo_path = os.path.join(logo_dir, f"{customer_name}.png")
            with open(logo_path, "wb") as f:
                f.write(image_bytes)
            return logo_path
        except Exception as e:
            logging.exception("❌ Fehler beim Speichern des Logos")
            return None
