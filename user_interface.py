
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
        self.selected_account = None
        self.cmd = None
        self.commands = {
            "1": self.login.start,
            "2": self.register_page,
            "3": self.account_manager.get_user_accounts,
            "send": self.send_execute,
            "inbox": self.receive_execute,
            "add acc": self.account_manager.login,
            "logout": self.initial_page,
            "help": self.help,
            "quit": self.exit_app
        }

    def initial_page(self) -> None:
        self.cmd = str(input("1- Sign in \n2- Register \n"))
        if self.cmd in ["1", "2", "quit"]:
            self.commands.get(self.cmd)()
        else:
            print("Choose 1 or 2")
            self.initial_page()

        if self.login.role.get('user'):
            self.view_accounts()

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
    def help() -> None:
        print("send -> sends an email\ninbox -> opens the inbox\nadd acc -> adds an email account\nlogout -> logs the user out\nquit -> closes the app")

    @staticmethod
    def welcome_page() -> None:
        welcome_text = Figlet(font="starwars")
        print(colored(welcome_text.renderText('MY     MAIL     SYSTEM'), 'green'))
        print("Enter help to list commands.")

    def register_page(self) -> None:
        register = db_file.Register()
        try:
            register.start()
        except Exception as e:
            print("Something went wrong please try again")
            print(f"{e.__class__ = }")
            self.register_page()
        else:
            self.initial_page()

    @staticmethod
    def exit_app() -> None:
        print("Thanks for using our app")
        exit(0)

    def router(self) -> None:
        self.welcome_page()
        self.initial_page()
        while True:
            self.cmd = str(input("-- "))
            if self.cmd == "add acc":
                self.commands.get(self.cmd)(username=self.login.username)
            elif self.cmd in self.commands:
                self.commands.get(self.cmd)()
            elif self.cmd == "1" or self.cmd == "2" or self.cmd == "3":
                print("Wrong command, Enter help to list commands.")
            else:
                print("Wrong command, Enter help to list commands.")


if __name__ == '__main__':
    AppInterface().router()
