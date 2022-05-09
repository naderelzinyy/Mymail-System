import sqlite3 as sql
from abc import ABC
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

    def unreturnable_execute(self, query: str, data=None):
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
    def __init__(self):
        self.__first_name = None
        self.__last_name = None
        self.__username = None
        self.__password = None
        self.__dob = None
        self.__email = None
        self.database = Database()

    def __set_name(self):
        pass

    def __set_email(self):
        pass

    def __set_username(self):
        pass

    def __set_password(self):
        pass

    def __set_dob(self):
        pass

    def __username_check(self, username):
        pass

    def __email_check(self, email):
        pass

    def __create_new_user(self):
        pass

    def execute(self):
        pass


class Register(User):
    def __init__(self):
        super().__init__()
        self.db = Database()

    def __set_name(self):
        self.__first_name = str(input("Enter first name: "))
        self.__last_name = str(input("Enter last name: "))

    def __set_username(self):
        username = str(input("Enter username: "))
        if self.__username_check(username):
            self.__username = username
        else:
            print('The username you entered is taken please try another one')
            self.__set_username()

    def __set_password(self):
        self.__password = str(input("Enter password: "))

    def __set_email(self):
        email = str(input("Enter email: "))
        if self.__email_check(email):
            self.__email = email
        else:
            print('The email you entered is used')
            self.__set_email()

    def __set_dob(self):
        self.__dob = str(input("Enter date of birth: "))

    def __username_check(self, username):
        usernames = [row[0] for row in self.db.returnable_execute("SELECT username FROM user", iteratable=True)]
        if username in usernames:
            return False

        return True

    def __email_check(self, email):
        emails = [row[0] for row in self.db.returnable_execute("SELECT email FROM user", iteratable=True)]
        if email in emails:
            return False
        return True

    def __create_new_user(self):
        new_user_credentials = [self.__first_name,
                                self.__last_name,
                                self.__username,
                                self.__password,
                                self.__dob,
                                self.__email]
        try:
            self.db.unreturnable_execute(
                "INSERT INTO user(first_name, last_name, username, password, dob, email) values (?,?,?,?,?,?)",
                data=[new_user_credentials])
        except Exception as e:
            print(e)
        else:
            print('Successfully registered!')

    def execute(self):
        self.__set_name()
        self.__set_username()
        self.__set_email()
        self.__set_password()
        self.__set_dob()
        self.__create_new_user()


class Login(User):
    def __init__(self):
        super().__init__()
        self.db = Database()

    def __set_name(self):
        pass

    def __set_username(self):
        self.__username = str(input("Enter username: "))

    def __set_password(self):
        self.__password = str(input("Enter password: "))

    def __set_login_credentials(self):
        self.__set_username()
        self.__set_password()
        if not self.__authenticate(self.__username, self.__password):
            print('wrong username or password!')
            self.__set_login_credentials()
        else:
            print('logged in!!')

    def __set_email(self):
        pass

    def __set_dob(self):
        pass

    @staticmethod
    def __authenticate(username: str, password: str) -> bool:
        # pwd = db.returnable_execute(f"SELECT password FROM user WHERE username = ?", data=username, iteratable=False)
        pwd = None
        with db.database_connection() as cursor:
            pwd = str(cursor.execute("SELECT password FROM user WHERE username = ?", (username,)).fetchone()).strip("('',)'")
        if pwd == password:
            return True
        else:
            return False

    def execute(self):
        self.__set_login_credentials()


if __name__ == '__main__':
    db = Database()
    register = Register()
    login = Login()
    # register.execute()
    login.execute()
    # db.execute("CREATE TABLE IF NOT EXISTS 'user' ('user_id' INTEGER NOT NULL , 'first_name'	TEXT"
    #            "NOT NULL, 'last_name'	" "TEXT NOT NULL, 'username' TEXT NOT NULL, 'password'	TEXT NOT NULL, "
    #            "'dob' TEXT NOT "
    #            "NULL, 'email'	TEXT NOT " "NULL, PRIMARY KEY('user_id' AUTOINCREMENT))")
    #
    # db.execute("CREATE TABLE IF NOT EXISTS 'emails' ("
    #            "'email_id'	INTEGER NOT NULL ,"
    #            "'email' TEXT NOT NULL,"
    #            "'email_password' TEXT NOT NULL,"
    #            "'user_id' INTEGER,"
    #            "PRIMARY KEY('email_id' AUTOINCREMENT),"
    #            "FOREIGN KEY('user_id') REFERENCES 'user'('user_id'))")
    #
    # db.execute("CREATE TABLE IF NOT EXISTS 'clients' ("
    #            "'client_id'	INTEGER NOT NULL ,"
    #            "'client_name'	TEXT NOT NULL,"
    #            "PRIMARY KEY('client_id' AUTOINCREMENT))")
    #
    # db.execute("CREATE TABLE IF NOT EXISTS 'user_clients' ("
    #            "'user_id'	INTEGER ,"
    #            "'client_id'	INTEGER,"
    #            "FOREIGN KEY('user_id') REFERENCES 'user'('user_id'),"
    #            "FOREIGN KEY('client_id') REFERENCES 'clients'('client_id'))")

    # db.execute("INSERT INTO user(first_name, last_name, username, password, dob, email) values (?,?,?,?,?,?)",
    #            data=users_data)
    # db.execute("INSERT INTO clients (client_name) values (?)", data=clients)
    #
    # db.select_execute("clients")
