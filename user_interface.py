
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
            3: self.account_manager.get_user_accounts,
            4: self.account_manager.login,
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
        self.choice = int(input("3- View email clients \n4- Add new email client \n5- Send an email \n6- Open inbox"))
        if self.choice == 3:
            self.view_accounts()
        elif self.choice == 4:
            self.scenarios.get(self.choice)(username=self.login.username)
        elif self.choice == 5:
            pass
        else:
            print("Choose 3 or 4")
            self.main_page()

    def choose_mail_client_page(self):
        pass

    def view_accounts(self):
        accounts = self.scenarios.get(self.choice)(username=self.login.username)
        print("\n\n\nYour email accounts : ")
        for account in accounts:
            print(accounts.index(account)+1, "- "+account[0])

    def register_page(self):
        register = db_file.Register()
        register.execute()

    def router(self) -> None:
        pass


if __name__ == '__main__':
    ui = Interface()
    ui.initial_page()
