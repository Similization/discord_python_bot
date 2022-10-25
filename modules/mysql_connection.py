from typing import Optional

import mysql.connector
from mysql.connector import MySQLConnection, OperationalError
from mysql.connector.cursor import MySQLCursor


class DataBaseManager:
    def __init__(self, config):
        self.config = config
        self.connection: Optional[MySQLConnection] = None
        self.cursor: Optional[MySQLCursor] = None

    def __enter__(self) -> Optional[MySQLCursor]:
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            return self.cursor
        except OperationalError as err:
            if err.args[0] == 1045:
                print("Invalid login or password")
            elif err.args[0] == 1049:
                print("Check database name")
            else:
                print(err)
            return None

    def __exit__(self, exc_type, exc_val, exc_tr) -> bool:
        if exc_type:
            print(f"Error type: {exc_type.__name__}")
            print(f"DB error: {' '.join(exc_val.args)}")

        if self.conn and self.cursor:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
            self.cursor.close()
        return True

    def query(self, sql, args) -> MySQLCursor:
        cursor = self.connection.cursor()
        cursor.execute(sql, args)
        return cursor

    def insert(self, sql, args) -> int:
        cursor = self.query(sql, args)
        last_element_id = cursor.lastrowid
        self.connection.commit()
        cursor.close()
        return last_element_id

    def insert_many(self, sql, args) -> int:
        cursor = self.connection.cursor()
        cursor.executemany(sql, args)
        rowcount = cursor.rowcount
        self.connection.commit()
        cursor.close()
        return rowcount

    def update(self, sql, args) -> int:
        cursor = self.query(sql, args)
        rowcount = cursor.rowcount
        self.connection.commit()
        cursor.close()
        return rowcount

    # def fetch(self, sql, args):
    #     rows = []
    #     cursor = self.query(sql, args)
    #     if cursor.with_rows:
    #         rows = cursor.fetchall()
    #     cursor.close()
    #     return rows
    #
    # def fetch_one(self, sql, args):
    #     row = None
    #     cursor = self.query(sql, args)
    #     if cursor.with_rows:
    #         row = cursor.fetchone()
    #     cursor.close()
    #     return row

    def __del__(self):
        if self.connection is not None:
            self.connection.close()
