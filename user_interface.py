
import database as db_file
import app as app_file


class Interface:
    def __init__(self):
        self.login = db_file.Login()
        self.register = db_file.Register()
        self.account_manager = app_file.EmailAccountManager()
        self.choice = None
        self.scenarios = {
            1: self.login.execute,
            2: self.register.execute,
            3: self.account_manager.login
        }

    def initial_page(self) -> None:
        self.choice = int(input("1- Sign in \n2- Register \n"))
        if self.choice == 1 or self.choice == 2:
            self.scenarios.get(self.choice)()
        else:
            print("Choose 1 or 2")
            self.initial_page()

        if self.login.role.get('user'):
            self.main_page()

    def main_page(self) -> None:
        self.choice = int(input("3- view email clients \n4- add new email client \n"))
        if self.choice == 3 or self.choice == 4:
            self.scenarios.get(self.choice)(username = self.login.username)
        else:
            print("Choose 3 or 4")
            self.main_page()

    def register_page(self):
        register = db_file.Register()
        register.execute()

    def router(self) -> None:
        pass


if __name__ == '__main__':
    ui = Interface()
    ui.initial_page()
