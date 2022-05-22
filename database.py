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


class UserSession(ABC):
    @abstractmethod
    def _set_name(self):
        pass

    @abstractmethod
    def _set_email(self):
        pass

    @abstractmethod
    def _set_username(self):
        pass

    @abstractmethod
    def _set_password(self):
        pass

    @abstractmethod
    def _set_date_of_birth(self):
        pass

    @abstractmethod
    def _username_check(self, username):
        pass

    @abstractmethod
    def _email_check(self, email):
        pass

    @abstractmethod
    def execute(self):
        pass


class Register(UserSession):
    def __init__(self):
        super().__init__()
        self.db = Database()

    def _set_name(self) -> None:
        self.first_name = str(input("Enter first name: "))
        self.last_name = str(input("Enter last name: "))

    def _set_username(self) -> None:
        username = str(input("Enter username: "))
        if self._username_check(username):
            self.username = username
        else:
            print('The username you entered is taken please try another one')
            self._set_username()

    def _set_password(self) -> None:
        self.password = str(input("Enter password: "))

    def _set_email(self) -> None:
        email = str(input("Enter email: "))
        if self._email_check(email):
            self.email = email
        else:
            print('The email you entered is used')
            self._set_email()

    def _set_date_of_birth(self) -> None:
        self.dob = str(input("Enter date of birth: "))

    def _username_check(self, username) -> bool:
        usernames = [row[0] for row in self.db.returnable_execute("SELECT username FROM user", iteratable=True)]
        return not (username in usernames)

    def _email_check(self, email) -> bool:
        emails = [row[0] for row in self.db.returnable_execute("SELECT email FROM user", iteratable=True)]
        return not (email in emails)

    def __create_new_user(self) -> None:
        new_user_credentials = [self.first_name,
                                self.last_name,
                                self.username,
                                self.password,
                                self.dob,
                                self.email]
        try:
            self.db.unreturnable_execute(
                "INSERT INTO user(first_name, last_name, username, password, dob, email) values (?,?,?,?,?,?)",
                data=[new_user_credentials])
        except Exception as e:
            print(e)
        else:
            print('Successfully registered!')

    def execute(self) -> None:
        self._set_name()
        self._set_username()
        self._set_email()
        self._set_password()
        self._set_date_of_birth()
        self.__create_new_user()


class Login(UserSession):
    def __init__(self):
        super().__init__()
        self.username = None
        self.password = None
        self.__db = Database()
        self.role = {
            'user': False,
            'admin': False
        }

    def _set_username(self) -> None:
        self.username = str(input("Enter username: "))

    def _set_password(self) -> None:
        self.password = str(input("Enter password: "))

    def __set_login_credentials(self) -> None:
        self._set_username()
        self._set_password()
        if not self.__authenticate(self.username, self.password):
            print('wrong username or password!')
            self.__set_login_credentials()
        else:
            self.username = self.username
            self.password = self.password
            self.role['user'] = True
            print('logged in!!')

    def _username_check(self, username) -> None:
        pass

    def _email_check(self, email) -> None:
        pass

    def _set_name(self) -> None:
        with self.__db.database_connected() as cursor:
            self.first_name = str(cursor.execute("SELECT first_name FROM user WHERE username = ?", (self.username,)).fetchone()).strip("('',)'")
            self.last_name = str(cursor.execute("SELECT last_name FROM user WHERE username = ?", (self.username,)).fetchone()).strip("('',)'")

    def _set_email(self) -> None:
        with self.__db.database_connected() as cursor:
            self.email = str(cursor.execute("SELECT email FROM user WHERE username = ?", (self.username,)).fetchone()).strip("('',)'")

    def _set_date_of_birth(self) -> None:
        with self.__db.database_connected() as cursor:
            self.dob = str(cursor.execute("SELECT date(dob) FROM user WHERE username = ?", (self.username,)).fetchone()).strip("('',)'")

    def __authenticate(self, username: str, password: str) -> bool:
        # pwd = db.returnable_execute(f"SELECT password FROM user WHERE username = ?", data=username, iteratable=False)
        with self.__db.database_connected() as cursor:
            pwd = str(cursor.execute("SELECT password FROM user WHERE username = ?", (username,)).fetchone()).strip("('',)'")
            return pwd == password

    def execute(self) -> None:
        self.__set_login_credentials()
        if self.role.get('user'):
            self._set_name()
            self._set_email()
            self._set_date_of_birth()
        else:
            self.execute()
