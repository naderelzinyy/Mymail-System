import sqlite3 as sql
from abc import ABC, abstractmethod
from contextlib import contextmanager


class Database:
    def __init__(self):
        self.connection = None

    @contextmanager
    def database_connection(self) -> None:
        self.connection = sql.connect("MyMail.db")
        cursor = self.connection.cursor()
        try:
            yield cursor
        except Exception as e:
            print(e)
        finally:
            self.connection.commit()
            self.connection.close()

    def unreturnable_execute(self, query: str, data=None) -> None:
        with self.database_connection() as cursor:
            if data is not None:
                cursor.executemany(query, data)
            else:
                cursor.execute(query)

    def returnable_execute(self, query: str, iteratable: bool, data=None):
        with self.database_connection() as cursor:
            if iteratable:
                result = [row for row in cursor.execute(query)]
                return result
            result = cursor.execute(query, (data,))
        return result


class User(ABC):
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
    def _set_dob(self):
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


class Register(User):
    def __init__(self):
        super().__init__()
        self.db = Database()

    def _set_name(self):
        self.first_name = str(input("Enter first name: "))
        self.last_name = str(input("Enter last name: "))

    def _set_username(self):
        username = str(input("Enter username: "))
        if self._username_check(username):
            self.username = username
        else:
            print('The username you entered is taken please try another one')
            self._set_username()

    def _set_password(self):
        self.password = str(input("Enter password: "))

    def _set_email(self):
        email = str(input("Enter email: "))
        if self._email_check(email):
            self.email = email
        else:
            print('The email you entered is used')
            self._set_email()

    def _set_dob(self):
        self.dob = str(input("Enter date of birth: "))

    def _username_check(self, username):
        usernames = [row[0] for row in self.db.returnable_execute("SELECT username FROM user", iteratable=True)]
        if username in usernames:
            return False

        return True

    def _email_check(self, email):
        emails = [row[0] for row in self.db.returnable_execute("SELECT email FROM user", iteratable=True)]
        if email in emails:
            return False
        return True

    def __create_new_user(self):
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

    def execute(self):
        self._set_name()
        self._set_username()
        self._set_email()
        self._set_password()
        self._set_dob()
        self.__create_new_user()


class Login(User):
    def __init__(self):
        super().__init__()
        self.username = None
        self.password = None
        self.__db = Database()
        self.__role = {
            'user': False,
            'admin': False
        }

    def _set_username(self):
        self.username = str(input("Enter username: "))

    def _set_password(self):
        self.password = str(input("Enter password: "))

    def __set_login_credentials(self):
        self._set_username()
        self._set_password()
        if not self.__authenticate(self.username, self.password):
            print('wrong username or password!')
            self.__set_login_credentials()
        else:
            self.username = self.username
            self.password = self.password
            self.__role['user'] = True
            print('logged in!!')

    def _username_check(self, username):
        pass

    def _email_check(self, email):
        pass

    def _set_name(self):
        with self.__db.database_connection() as cursor:
            self.first_name = str(cursor.execute("SELECT first_name FROM user WHERE username = ?", (self.username,)).fetchone()).strip("('',)'")
            self.last_name = str(cursor.execute("SELECT last_name FROM user WHERE username = ?", (self.username,)).fetchone()).strip("('',)'")

    def _set_email(self):
        with self.__db.database_connection() as cursor:
            self.email = str(cursor.execute("SELECT email FROM user WHERE username = ?", (self.username,)).fetchone()).strip("('',)'")

    def _set_dob(self):
        with self.__db.database_connection() as cursor:
            self.dob = str(cursor.execute("SELECT date(dob) FROM user WHERE username = ?", (self.username,)).fetchone()).strip("('',)'")

    def __authenticate(self, username: str, password: str) -> bool:
        # pwd = db.returnable_execute(f"SELECT password FROM user WHERE username = ?", data=username, iteratable=False)
        with self.__db.database_connection() as cursor:
            pwd = str(cursor.execute("SELECT password FROM user WHERE username = ?", (username,)).fetchone()).strip("('',)'")
        if pwd == password:
            return True
        else:
            return False

    def execute(self):
        self.__set_login_credentials()
        if self.__role.get('user'):
            self._set_name()
            self._set_email()
            self._set_dob()

    def show_user_info(self):
        print(self.first_name, self.last_name, self.username, self.password, self.dob, self.email)


class UserAccounts:
    def __init__(self):
        self.email = None
        self.password = None

    def __set_email(self):
        self.email = str(input("Enter Email : "))

    def __set_password(self):
        self.password = str(input("Enter password : "))

    def __set_account_credentials(self):
        pass

    def __store_account_credentials(self):
        pass


if __name__ == '__main__':
    db = Database()
    register = Register()
    login = Login()
    # register.execute()
    login.execute()
    login.show_user_info()
