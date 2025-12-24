import sqlite3
from typing import Optional

class SQLiteManager:
    def __init__(self, db_file):
        self.conn   = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS hbpdata (
                play_id TEXT PRIMARY KEY,
                game_pk INTEGER NOT NULL,
                pitcher_id INTEGER NOT NULL,
                batter_id INTEGER NOT NULL,
                end_speed REAL NOT NULL,
                x_pos REAL NOT NULL,
                z_pos REAL NOT NULL,
                downloaded INTEGER NOT NULL DEFAULT 0,
                analyzed INTEGER NOT NULL DEFAULT 0,
                skeeted INTEGER NOT NULL DEFAULT 0
            )
        """)
        self.conn.commit()

    def insert_hbpdata(self, play_id: str, game_pk: int, pitcher_id: int, batter_id: int, end_speed: float, x_pos: float, z_pos: float, downloaded: Optional[bool] = False) -> bool:
        insert_result = False
        try:
            self.cursor.execute(
                "INSERT INTO hbpdata (play_id, game_pk, pitcher_id, batter_id, end_speed, x_pos, z_pos, downloaded) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                (play_id, game_pk, pitcher_id, batter_id, end_speed, x_pos, z_pos, downloaded)
            )
            self.conn.commit()
            insert_result = True
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        return insert_result
    
    def get_hbpdata_data(self, query: str, args: list) -> list:
        self.cursor.execute(query, args)
        records = self.cursor.fetchall()
        return records

    def read_hbpdata_all(self) -> list:
        self.cursor.execute(f"SELECT * FROM hbpdata")
        records = self.cursor.fetchall()
        return records
    
    def update_hbpdata_data(self, query: str,  args: list) -> list:
        self.cursor.execute(query, args)
        self.conn.commit() 
        return self.cursor.rowcount

    def close_connection(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()