import sqlite3

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
                y_pos REAL NOT NULL
            )
        """)
        self.conn.commit()

    def insert_hbpdata(self, play_id: str, game_pk: int, pitcher_id: int, batter_id: int, end_speed: float, x_pos: float, y_pos: float) -> bool:
        insert_result = False
        try:
            self.cursor.execute(
                "INSERT INTO hbpdata (play_id, game_pk, pitcher_id, batter_id, end_speed, x_pos, y_pos) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                (play_id, game_pk, pitcher_id, batter_id, end_speed, x_pos, y_pos)
            )
            self.conn.commit()
            insert_result = True
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        return insert_result

    def read_hbpdata_all(self) -> list:
        self.cursor.execute(f"SELECT * FROM hbpdata")
        records = self.cursor.fetchall()
        return records
    
    def get_hbpdata_data(self, query: str, args: list) -> list:
        self.cursor.execute(query, args)
        records = self.cursor.fetchall()
        return records

    def close_connection(self):
        self.conn.close()
        print("Sqlite3 database connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()

## Example usage:
## db_dir      = config.get("paths", "db_dir")
## db_filename = config.get("database", "hbp_db_filename")
## db_table    = config.get("database", "hbp_table")
## db_file_path = Path(db_dir, db_filename)
## print(f"Writing to {db_table} to file '{db_file_path}'.")

## with SQLiteManager(db_filename) as db: 
##     db.insert_hbpdata(str(uuid.uuid4()), 111111, 222222, 333333, 86.7, 3.14, 6.28)
##     db.insert_hbpdata(str(uuid.uuid4()), 444444, 555555, 666666, 92.1, 14.5, 9.01)
##     db.insert_hbpdata(str(uuid.uuid4()), 777777, 888888, 999999, 95.5, 7.77, 19.77)

##     all_data = db.read_hbpdata_all()
##     print("All data:")
##     pprint.pprint(all_data)
##     print()

##     select_data = db.get_hbpdata_data(
##         f"SELECT * FROM {db_table} WHERE game_pk = ?",
##         [444444]
##     )
##     print("Just some of the data:")
##     pprint.pprint(select_data)

