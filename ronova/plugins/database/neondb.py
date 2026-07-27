import psycopg2
from config import POSTGRE_KEY


class HandleDb:
    def __init__(self, POSTGRE_KEY: str):
        self.POSTGRE_KEY = POSTGRE_KEY
        self.conn = None
        self.cur = None

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(self.POSTGRE_KEY)
            self.conn.autocommit = True
            self.cur = self.conn.cursor()

    def close(self):
        if self.cur:
            self.cur.close()
            self.cur = None
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, command: str, params=None, fetch=False):
        try:
            self.connect()
            self.cur.execute(command, params)
            if fetch:
                return self.cur.fetchall()
        except Exception as e:
            print(f"Error:\n{e}")
            raise


db = HandleDb(POSTGRE_KEY)