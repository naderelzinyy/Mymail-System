import re

import database as db_file
import email_clients as mail_clients

from email import encoders
from termcolor import colored
from datetime import datetime
from tkinter import filedialog
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup as bs
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Email(ABC):
    mail_clients = {
        'outlook': mail_clients.OutlookClient,
        'hotmail': mail_clients.OutlookClient,
        'yahoo': mail_clients.YahooMailClient,
        'gmail': mail_clients.GmailClient,
        'yandex': mail_clients.YandexClient,
        'icloud': mail_clients.IcloudClient,
    }

    @abstractmethod
    def get_domain_name(self):
        pass

    @abstractmethod
    def set_password(self):
        pass

    @abstractmethod
    def set_mail_client(self):
        pass

    @abstractmethod
    def login(self, username: str = None):
        pass

    @abstractmethod
    def store_emails(self):
        pass

    @abstractmethod
    def _html_to_text(self, message: str) -> str:
        pass


class EmailAccountManager(Email):
    """
    - Stores the accounts of each user in the Database.
    - Views the accounts of each user
    """

    def __init__(self):
        self.__mail_client = None
        self.email = None
        self.password = None
        self.domain_name = None
        self.account_valid = False

    def set_email(self) -> None:
        self.email = str(input("Enter Email : "))

    def set_password(self) -> None:
        self.password = str(input("Enter password : "))

    def get_domain_name(self) -> str:
        domain = re.search("[@-][\w]+", self.email).group()
        self.domain_name = domain[1:]
        return self.domain_name

    def set_mail_client(self) -> None:
        selected_mail_client = self.get_domain_name()
        self.__mail_client = super().mail_clients.get(selected_mail_client)

    def set_credentials(self) -> None:
        self.set_email()
        self.set_password()

    def login(self, username: str = None) -> None:
        """
        Checks if the credentials are valid or not.
        """
        self.set_credentials()
        self.set_mail_client()
        mail_client_connection = self.__mail_client().ssl_connected
        tls_clients = [mail_clients.OutlookClient, mail_clients.IcloudClient]
        if self.__mail_client in tls_clients:
            mail_client_connection = self.__mail_client().tls_connected

        with mail_client_connection(self.email, self.password, action=self.login):
            self.account_valid = True
            print("Account authenticated !")
            self.__store_account_credentials(username=username)

    def __store_account_credentials(self, username: str) -> None:
        db = db_file.Database()
        with db.database_connected() as cursor:
            user_id = str(cursor.execute("SELECT user_id FROM user WHERE username = ?", (username,)).fetchone()).strip(
                "('',)'")
            client_id = str(cursor.execute("SELECT client_id FROM clients WHERE client_name = ?",
                                           (self.domain_name,)).fetchone()).strip("('',)'")
            cursor.execute("INSERT INTO user_accounts (email, email_password, user_id, client_id) VALUES (?,?,?,?)",
                           (self.email, self.password, user_id, client_id))

    @staticmethod
    def get_user_accounts(username: str) -> list:
        db = db_file.Database()
        with db.database_connected() as cursor:
            user_id = str(cursor.execute("SELECT user_id FROM user WHERE username = ?", (username,)).fetchone()) \
                .strip("('',)'")
            accounts = [row for row in cursor.execute("SELECT email FROM user_accounts WHERE user_id = ?", (user_id,))]
        return accounts

    def store_emails(self) -> None:
        pass

    def _html_to_text(self, message: str) -> str:
        pass


class EmailSender(Email):
    def __init__(self):
        super().__init__()
        self.__subject = None
        self.__from = None
        self.__to = None
        self.__password = None
        self.__message = """
        <html>
            <body>
                <p>{}</p>
            </body>
        </html>
        """
        self.__headers = None
        self.__mail_client = None
        self.__file_name = None
        self.__file_types = [('PDF files', '*.pdf'),
                             ('JPG files', '*.jpg'),
                             ('PNG files', '*.png'),
                             ('Python Files', '*.py'),
                             ('all files', '.*')]

    def set_password(self, password: str = None) -> None:
        self.__password = password

    def set_sender(self, sender: str) -> None:
        self.__from = sender

    def set_recipient(self) -> None:
        self.__to = str(input("Enter recipient email: "))

    def set_subject(self) -> None:
        self.__subject = str(input("Enter subject content: "))

    def set_message(self) -> None:
        message = str(input("Enter email content: "))
        self.__message = self.__message.format(message)
        self.__message = self._html_to_text(self.__message)

    def set_attachment(self) -> MIMEBase:
        self.__file_name = filedialog.askopenfilename(title="Open a Text File", filetypes=self.__file_types)
        self.__headers = ("Content-Disposition", f"attachment; filename= {format(self.__file_name)}")
        with open(self.__file_name, 'rb') as attachment:
            attach = MIMEBase('application', 'octet-stream')
            attach.set_payload(attachment.read())
        encoders.encode_base64(attach)
        attach.add_header(self.__headers[0], self.__headers[1])
        return attach

    def __mail_init(self) -> MIMEMultipart:
        mail_content = MIMEMultipart('alternative')
        mail_content["Subject"] = self.__subject
        mail_content["From"] = self.__from
        mail_content["To"] = self.__to
        mail_content.attach(MIMEText(self.__message, 'html'))
        attachment_req = str(input(" Do you want to add an attachment ? (y/n) "))
        if attachment_req == "y":
            mail_content.attach(self.set_attachment())
        return mail_content

    def get_domain_name(self) -> str:
        domain = re.search("[@-][\w]+", self.__from).group()
        domain_name = domain[1:]
        return domain_name

    def _html_to_text(self, message: str) -> str:
        message = bs(message, "html.parser").get_text("\n")
        return message

    def set_mail_client(self) -> None:
        selected_mail_client = self.get_domain_name()
        self.__mail_client = super().mail_clients.get(selected_mail_client)

    def __send_execute(self) -> None:
        mail_client_connection = self.__mail_client().ssl_connected
        if self.__mail_client == mail_clients.OutlookClient or self.__mail_client == mail_clients.IcloudClient:
            mail_client_connection = self.__mail_client().tls_connected

        with mail_client_connection(self.__from, self.__password) as connection:
            connection.sendmail(self.__from, self.__to, self.__mail_init().as_string())
            print(colored("Email successfully sent.", 'green'))
            self.store_emails()

    def login(self, sender: str = None) -> None:
        """ Login into the email client.
        """
        db = db_file.Database()

        with db.database_connected() as cursor:
            password = str(
                cursor.execute("SELECT email_password FROM user_accounts WHERE email = ?", (sender,)).fetchone()).strip(
                "('',)'")
        self.set_sender(sender)
        self.set_password(password=password)
        self.set_mail_client()

    def send(self) -> None:
        self.set_recipient()
        self.set_subject()
        self.set_message()
        self.__send_execute()

    def store_emails(self) -> None:
        db = db_file.Database()
        date_sent = str(datetime.now()) + str(datetime.today())
        with db.database_connected() as cursor:
            account_id = int(str(cursor.execute("SELECT account_id FROM user_accounts WHERE email = ?",
                                                (self.__from,)).fetchone()).strip("('',)'"))
            stored_email = [self.__from, self.__to, self.__message, self.__subject, date_sent, account_id, "sent"]
            cursor.executemany(
                "INSERT INTO emails (sender, recipient, message, title, date_sent, account_id, email_type)"
                " values (?,?,?,?,?,?,?) ", [stored_email])


class EmailReceiver(Email):
    def __init__(self):
        super().__init__()
        self.__email = None
        self.__password = None
        self.__mail_client = None
        self.received_emails = []

    def set_email(self, receiver: str) -> None:
        self.__email = receiver

    def set_password(self, password: str = None) -> None:
        self.__password = password

    def get_domain_name(self) -> str:
        domain = re.search("[@-][\w]+", self.__email).group()
        domain_name = domain[1:]
        return domain_name

    def set_mail_client(self) -> None:
        selected_mail_client = self.get_domain_name()
        self.__mail_client = super().mail_clients.get(selected_mail_client)

    def login(self, receiver: str = None) -> None:
        db = db_file.Database()
        with db.database_connected() as cursor:
            password = str(cursor.execute("SELECT email_password FROM user_accounts WHERE email = ?",
                                          (receiver,)).fetchone()).strip("('',)'")
        self.set_email(receiver)
        self.set_password(password=password)
        self.set_mail_client()

    def _html_to_text(self, message: str) -> str:
        message = bs(message, "html.parser").get_text("\n")
        return message

    def receive_unseen_emails(self) -> None:
        mail_client_connection = self.__mail_client().imap_connected
        with mail_client_connection(self.__email, self.__password) as connection:
            self.received_emails = list(connection.unseen())
            if self.received_emails:
                self.store_emails()
                for mail in self.received_emails:
                    print(self.received_emails.index(mail) + 1, "- From : " + mail.from_addr, "|| ", mail.title)
            else:
                print("No new emails !")
                # # Converting html to text function
                # message = self.__html_to_text(rec_email[0].body)
                # # for title
                # print("Email title: ", str(rec_email[0].title))
                # # for the sender’s email address
                # print("From : ", rec_email.from_addr)
                # # for the main content of the email
                # print("\n\n", message)
                # # for any type of attachment
                # if rec_email.attachments:
                #     print("Attachment : ", rec_email.attachments)
                # print("Date: ", rec_email.date)

    def get_unseen_emails_number(self, email: str) -> int:
        db = db_file.Database()
        with db.database_connected() as cursor:
            password = str(
                cursor.execute("SELECT email_password FROM user_accounts WHERE email = ?", (email,)).fetchone()).strip(
                "('',)'")
        self.login(email)
        mail_client_connection = self.__mail_client().imap_connected
        with mail_client_connection(email, password, read_only=True) as connection:
            emails = list(connection.unseen())
        return len(emails)

    def store_emails(self) -> None:
        db = db_file.Database()
        with db.database_connected() as cursor:
            account_id = int(str(cursor.execute("SELECT account_id FROM user_accounts WHERE email = ?",
                                                (self.__email,)).fetchone()).strip("('',)'"))
            for mail in self.received_emails:
                message = self._html_to_text(mail.body)
                stored_email = [mail.from_addr, mail.to, message, mail.title, mail.date, account_id, "received"]
                cursor.executemany(
                    "INSERT INTO emails (sender, recipient, message, title, date_sent, account_id, email_type)"
                    " values (?,?,?,?,?,?,?) ", [stored_email])
