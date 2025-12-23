import mysql.connector


class DatabaseConnector:
    def __init__(self, hostname, database, username, password):
        """
        Initialize the DatabaseConnection with database settings pulled from a
        settings config file.

        :param hostname: Hostname of target MySQL server.
        :param database: Working database on target MySQL server.
        :param username: Username of MySQL user who can access the working database.
        :param password: Password of MySQL user.
        """
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Connect to the database in question.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.hostname,
                database=self.database,
                user=self.username,
                password=self.password,
            )
            self.cursor = self.connection.cursor()
            print("Database connection established successfully.")
        except mysql.connector.Error as err:
            print(f"[ERROR] Can't connect to database: {err}")
            self.connection = None
            self.cursor = None

    def disconnect(self):
        """
        Disconnect to the database in question.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query, params=None):
        """
        Execute a MySQL query with the provided parameters.

        :param query: Query to run on target MySQL server.
        :param params: Parameters to be passed into query.
        """
        if not self.connection or not self.cursor:
            print("[WARNING] No active database connection.")
            return None
        try:
            self.cursor.execute(query, params)
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.connection.commit()
                print("Query executed and committed.")
            else:
                return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"[ERROR] Problem executing query: {err}")
            self.connection.rollback()  # Rollback in case of error during transaction
            return None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
