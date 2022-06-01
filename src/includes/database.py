import mysql.connector


class Database:
    def __init__(self, config):
        # TODO: handle port forwarding
        #  https://medium.com/@amirziai/query-your-database-over-an-ssh-tunnel-with-pandas-603ce49b35a1
        #  https://stackoverflow.com/questions/12989866/python-ssh-tunnel-setup-and-mysql-db-access
        self.dbhost = config.get("DBHOST")
        self.dbport = config.get("DBPORT")
        self.dbname = config.get("DBNAME")
        self.dbuser = config.get("DBUSER")
        self.dbpass = config.get("DBPASS")
        if (
            not self.dbhost
            or not self.dbport
            or not self.dbname
            or not self.dbuser
            or not self.dbpass
        ):
            raise ImportError("Missing database configuration parameters")

        self._conn = mysql.connector.connect(
            host=self.dbhost,
            port=self.dbport,
            database=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
        )
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()
