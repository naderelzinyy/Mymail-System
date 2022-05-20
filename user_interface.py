
import database as db_file
import app as app_file
from termcolor import colored
from pyfiglet import Figlet


class AppInterface:
    def __init__(self):
        self.login = db_file.Login()
        self.register = db_file.Register()
        self.account_manager = app_file.EmailAccountManager()
        self.email_sender = app_file.EmailSender()
        self.email_receiver = app_file.EmailReceiver()
        self.choice = None
        self.selected_account = None
        self.scenarios = {
            "4": self.account_manager.login,
            "5": self.send_execute,
            "6": self.receive_execute,
        }

        self.commands = {
            "1": self.login.execute,
            "2": self.register.execute,
            "3": self.account_manager.get_user_accounts,
            "send": self.send_execute,
            "inbox": self.receive_execute,
            "add acc": self.account_manager.login,
            "logout": self.initial_page,
            "quit": self.exit_app
        }
        self.cmd = None

    def initial_page(self) -> None:

        self.cmd = str(input("1- Sign in \n2- Register \n"))
        if self.cmd == "1" or self.cmd == "2":
            self.commands.get(self.cmd)()
        elif self.choice == "quit":
            self.commands.get("quit")()
        else:
            print("Choose 1 or 2")
            self.initial_page()

    @staticmethod
    def welcome_page():
        welcome_text = Figlet(font="starwars")
        print(colored(welcome_text.renderText('MY     MAIL     SYSTEM'), 'green'))

    # def main_page(self) -> None:
    #     self.view_accounts()
    #     print("\n")
    #     self.choice = str(input("3- View email clients \n4- Add new email client \n5- Send an email \n6- Open inbox \n"))
    #     if self.choice == "3":
    #         self.view_accounts()
    #     elif self.choice == "4":
    #         self.scenarios.get(self.choice)(username=self.login.username)
    #     elif self.choice == "5" or self.choice == "6":
    #         self.scenarios.get(self.choice)()
    #     else:
    #         print("Wrong value.\nPlease choose again.")
    #         self.main_page()

    def choose_mail_account_page(self) -> None:
        accounts = self.commands.get("3")(username=self.login.username)
        for account in accounts:
            print(accounts.index(account)+1, "- "+account[0])
        account_index = int(input("Choose an account : \n"))
        self.selected_account = accounts[account_index-1][0]

    def send_execute(self) -> None:
        self.choose_mail_account_page()
        self.email_sender.login(sender=self.selected_account)
        self.email_sender.send()

    def receive_execute(self) -> None:
        self.choose_mail_account_page()
        self.email_receiver.login(receiver=self.selected_account)
        self.email_receiver.receive_unseen_emails()

    def view_accounts(self) -> None:
        accounts = self.commands.get("3")(username=self.login.username)
        print("\n\n\nYour email accounts : ")
        status = "No new emails"
        for account in accounts:
            emails_number = self.email_receiver.get_unseen_emails_number(account[0])
            if emails_number > 0:
                status = "{} new emails".format(emails_number)
            print(accounts.index(account)+1, "- "+account[0], " || ", status)

    @staticmethod
    def register_page() -> None:
        register = db_file.Register()
        register.execute()

    @staticmethod
    def exit_app():
        print("Thanks for using our app")
        exit()

    def router(self) -> None:
        self.welcome_page()
        self.initial_page()
        self.view_accounts()
        while True:
            self.cmd = str(input("-- "))
            if self.cmd == "add acc":
                self.commands.get(self.cmd)(username=self.login.username)
            elif self.cmd in self.commands:
                self.commands.get(self.cmd)()
            else:
                print("Wrong command, Enter help to list commands.")


if __name__ == '__main__':
    ui = AppInterface()
    ui.router()
