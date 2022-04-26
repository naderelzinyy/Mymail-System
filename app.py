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


class MailClient:
    def __init__(self, port: int, host: str):
        self.port = port  # SSL Port
        self.host = host
        self.__connection_context = ssl.create_default_context()

    @contextmanager
    def server_connection(self, email: str, password: str) -> None:
        # Create a secure SSL context
        with smtp.SMTP_SSL(self.host, self.port, context=self.__connection_context) as mail_server:
            try:
                # mail_server.connect(email, self.port)
                mail_server.login(email, password)
                yield mail_server

            except smtp.SMTPAuthenticationError:
                print("E-mail and password are not accepted.")
            # except Exception as e:
            #     print('something went wrong')
            else:
                print('Connection successfully established')
            finally:
                mail_server.close()


class OutlookClient(MailClient):
    def __init__(self):
        super().__init__(port=465 , host="smtp.office365.com")


class YahooMailClient(MailClient):
    pass


class GmailClient(MailClient):
    def __init__(self):
        super().__init__(port=465, host="smtp.gmail.com")


class Email:
    def __init__(self):
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

    def __set_domain_name(self) -> str:
        domain = re.search("[@-][\w]+", self.__from).group()
        domain_name = domain[1:]
        return domain_name

    def __set_mail_client(self):
        mail_clients = {
            'outlook': OutlookClient,
            'yahoo': YahooMailClient,
            'gmail': GmailClient
        }
        selected_mail_client = self.__set_domain_name()
        self.__mail_client = mail_clients.get(selected_mail_client)

    def __send_execute(self) -> None:
        mail_client_connection = self.__mail_client().server_connection
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
        self.__set_mail_client()

    def send(self) -> None:
        self.set_recipient()
        self.set_subject()
        self.set_message()
        self.__send_execute()


# def send_email():
#     # mail_password = getpass.getpass("Password: ")
#     mail_password = 'PythonEmailTest'
#     sender_email = 'zidev.py@yahoo.com'
#     receiver_email = 'naderelziny805@gmail.com'
#     # message = 'Hello, this is a test email'
#     message = MIMEMultipart('alternative')
#     message["Subject"] = "Multipart Test2"
#     message["From"] = sender_email
#     message["To"] = receiver_email
#     # text = ""
#     html = """
#     <html>
#         <body>
#             <h1 style="color: red;">Hello</h1><br>
#             <p>This is zidev.py trying to send emails with python</p>
#         </body>
#     </html>
#
#     """
#
#     # part1 = MIMEText(text, 'plain')
#     part2 = MIMEText(html, 'html')
#     file_name = 'DHLdocument2.pdf'
#
#     with open(file_name, 'rb') as attachment:
#         part = MIMEBase('application', 'octet-stream')
#         part.set_payload(attachment.read())
#
#     encoders.encode_base64(part)
#     part.add_header(
#         "Content-Disposition",
#         "attachment; filename= Our Pdf Document",
#     )
#
#     # message.attach(part1)
#     message.attach(part)
#     message.attach(part2)
#
#     with server_connection(mail_password) as connection:
#         try:
#             connection.sendmail(sender_email, receiver_email, message.as_string())
#         except RuntimeError("generator didn't yield"):
#             pass


if __name__ == '__main__':
    try:
        email = Email()
        email.login()
        email.send()
    except RuntimeError as e:
        print(e)
    else:
        print('E-mail Successfully sent!')
