# backend/poseEstimation/player_manager.py
import pandas as pd
import os

class PlayerManager:
    def __init__(self):
        self.player_data_path = "backend/data/spieler.csv"
        self.players_df = self.load_players()

    def load_players(self):
        if os.path.exists(self.player_data_path):
            return pd.read_csv(self.player_data_path)
        else:
            return pd.DataFrame(columns=["spieler_id", "vorname", "nachname", "position", "team", "alter"])

    def save_new_player(self, player_data):
        self.players_df = self.players_df.append(player_data, ignore_index=True)
        self.players_df.to_csv(self.player_data_path, index=False)

    def get_players_for_team(self, team_name):
        return self.players_df[self.players_df["team"] == team_name]
