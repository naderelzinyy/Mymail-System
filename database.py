import sqlite3 as sql

from abc import ABC, abstractmethod
from contextlib import contextmanager


class Database:
    def __init__(self):
        self.connection = None

    @contextmanager
    def database_connected(self, action=lambda: None) -> None:
        self.connection = sql.connect("MyMail.db")
        cursor = self.connection.cursor()
        try:
            yield cursor
        except Exception as e:
            print(e)
            action()
        finally:
            self.connection.commit()
            self.connection.close()

    def unreturnable_execute(self, query: str, data=None) -> None:
        with self.database_connected() as cursor:
            if data is not None:
                cursor.executemany(query, data)
            else:
                cursor.execute(query)

    def returnable_execute(self, query: str, iteratable: bool, data=None):
        with self.database_connected() as cursor:
            if iteratable:
                result = [row for row in cursor.execute(query)]
                return result
            result = cursor.execute(query, (data,))
        return result
