import ssl

import smtplib as smtp
import easyimap as imap

from contextlib import contextmanager


class MailClient:
    def __init__(self, port: int, smtp_host: str, imap_host: str):
        self.port = port  # SSL Port
        self.smtp_host = smtp_host
        self.imap_host = imap_host
        self.__connection_context = ssl.create_default_context()

    @contextmanager
    def ssl_connected(self, email: str, password: str, action=lambda: None) -> None:
        # Create a secure SSL context
        with smtp.SMTP_SSL(self.smtp_host, self.port, context=self.__connection_context) as mail_server:
            try:
                # mail_server.connect(email, self.port)
                mail_server.login(email, password)
                yield mail_server
            except RuntimeError("generator didn't yield"):
                pass
            except smtp.SMTPAuthenticationError:
                print("Username and Password not accepted")
                action()
            finally:
                mail_server.close()

    @contextmanager
    def tls_connected(self, email: str, password: str, action=lambda: None) -> None:
        try:
            server = smtp.SMTP(host=self.smtp_host, port=self.port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(email, password)
            yield server
        except Exception as e:
            print("Authentication unsuccessful!")
            action()
        finally:
            server.close()

    @contextmanager
    def imap_connected(self, email: str, password: str, read_only=False, action=lambda: None) -> None:
        try:
            server = imap.connect(self.imap_host, email, password, ssl=True, port=993, read_only=read_only)
            yield server
        except Exception as e:
            print(e)
            action()
        finally:
            server.quit()


class OutlookClient(MailClient):
    def __init__(self):
        super().__init__(port=587, smtp_host="smtp.office365.com", imap_host="imap-mail.outlook.com")


class IcloudClient(MailClient):
    def __init__(self):
        super().__init__(port=587, smtp_host="smtp.mail.me.com", imap_host="imap.mail.me.com")


class YahooMailClient(MailClient):
    pass


class GmailClient(MailClient):
    def __init__(self):
        super().__init__(port=465, smtp_host="smtp.gmail.com", imap_host="imap.gmail.com")


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
        super().__init__(port=465, smtp_host="smtp.yandex.com", imap_host="imap.yandex.com")
