import smtplib as smtp
import ssl
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from contextlib import contextmanager
import re
from tkinter import filedialog
import easyimap as imap
from abc import ABC, abstractmethod


class MailClient:
    def __init__(self, port: int, smtp_host: str, imap_host: str):
        self.port = port  # SSL Port
        self.smtp_host = smtp_host
        self.imap_host = imap_host
        self.__connection_context = ssl.create_default_context()

    @contextmanager
    def ssl_connection(self, email: str, password: str) -> None:
        # Create a secure SSL context
        with smtp.SMTP_SSL(self.smtp_host, self.port, context=self.__connection_context) as mail_server:
            try:
                # mail_server.connect(email, self.port)
                mail_server.login(email, password)
                yield mail_server

            except smtp.SMTPAuthenticationError as e:
                print(e)
            else:
                print('Connection successfully established')
            finally:
                mail_server.close()

    @contextmanager
    def tls_connection(self, email: str, password: str) -> None:
        try:
            server = smtp.SMTP(host=self.smtp_host, port=self.port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(email, password)
            yield server
        except Exception as e:
            print(e)
        else:
            print('Connection successfully established')
        finally:
            server.close()

    @contextmanager
    def imap_connection(self, email: str, password: str):
        try:
            server = imap.connect(self.imap_host, email, password)
            yield server
        except Exception as e:
            print(e)
        else:
            print('Connection successfully established')
        finally:
            server.quit()


class OutlookClient(MailClient):
    def __init__(self):
        super().__init__(port=587, smtp_host="smtp.office365.com",imap_host="imap-mail.outlook.com")


class YahooMailClient(MailClient):
    pass


class GmailClient(MailClient):
    def __init__(self):
        super().__init__(port=465, smtp_host="smtp.gmail.com",imap_host="imap.gmail.com")


class YandexClient(MailClient):
    """
        Yandex user must generate a new password for the SMTP Connection.
        1- Go to (https://passport.yandex.com/profile).
        2- Click on "Passwords and authorization".
        3- Click on "Create new password" under "App passwords".
        4- Select "Email" and choose a name for your password.
        5- Copy the generated password and use it for logging in through Mymail.
    """

    def __init__(self):
        super().__init__(port=465, smtp_host="smtp.yandex.com",imap_host="imap.yandex.com")


class Email(ABC):
    mail_clients = {
        'outlook': OutlookClient,
        'hotmail': OutlookClient,
        'yahoo': YahooMailClient,
        'gmail': GmailClient,
        'yandex': YandexClient
    }

    @abstractmethod
    def set_domain_name(self):
        pass

    @abstractmethod
    def set_password(self):
        pass

    @abstractmethod
    def set_mail_client(self):
        pass

    @abstractmethod
    def login(self):
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

    def set_password(self) -> None:
        self.__password = str(input("Enter password: "))

    def set_sender(self) -> None:
        self.__from = str(input("Enter your email: "))

    def set_recipient(self) -> None:
        self.__to = str(input("Enter recipient email: "))

    def set_subject(self) -> None:
        self.__subject = str(input("Enter subject content: "))

    def set_message(self) -> None:
        message = str(input("Enter email content: "))
        self.__message = self.__message.format(message)

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
        mail_content.attach(self.set_attachment())
        return mail_content

    def set_domain_name(self) -> str:
        domain = re.search("[@-][\w]+", self.__from).group()
        domain_name = domain[1:]
        return domain_name

    def set_mail_client(self):

        selected_mail_client = self.set_domain_name()
        self.__mail_client = super().mail_clients.get(selected_mail_client)

    def __send_execute(self) -> None:
        mail_client_connection = self.__mail_client().ssl_connection
        if self.__mail_client == OutlookClient:
            mail_client_connection = self.__mail_client().tls_connection

        with mail_client_connection(self.__from, self.__password) as connection:
            try:
                connection.sendmail(self.__from, self.__to, self.__mail_init().as_string())
            except RuntimeError("generator didn't yield"):
                pass

    def login(self) -> None:
        """ Login into the email client.
        """
        self.set_sender()
        self.set_password()
        self.set_mail_client()

    def send(self) -> None:
        self.set_recipient()
        self.set_subject()
        self.set_message()
        self.__send_execute()


class EmailReceiver(Email):
    def __init__(self):
        super().__init__()
        self.__email = None
        self.__password = None
        self.__mail_client = None

    def set_email(self):
        self.__email = str(input("Enter Email: "))

    def set_password(self):
        self.__password = str(input("Enter Password: "))

    def set_domain_name(self):
        domain = re.search("[@-][\w]+", self.__email).group()
        domain_name = domain[1:]
        return domain_name

    def set_mail_client(self):
        selected_mail_client = self.set_domain_name()
        self.__mail_client = super().mail_clients.get(selected_mail_client)

    def login(self):
        self.set_email()
        self.set_password()
        self.set_mail_client()

    def receive(self) -> None:
        mail_client_connection = self.__mail_client().imap_connection
        with mail_client_connection(self.__email, self.__password) as connection:
            connection.listids()
            email = connection.mail(connection.listids()[3])
            # for title
            print(email.title)
            # for the sender’s email address
            print(email.from_addr)
            # for the main content of the email
            print(email.body)
            # for any type of attachment
            print(email.attachments)


if __name__ == '__main__':
    try:
        email = EmailSender()
        email.login()
        email.send()
    except RuntimeError as e:
        print(e)
    else:
        print('E-mail Successfully sent!')
