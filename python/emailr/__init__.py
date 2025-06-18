import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import settings

class EmailR:
    """
    A static class to send emails with HTML content using smtplib.
    """

    @staticmethod
    def send_email(receiver_email: str, subject: str, html_body: str) -> bool:
        """
        Sends an email with an HTML body.

        Args:
            receiver_email (str): The email address of the recipient.
            subject (str): The subject of the email.
            html_body (str): The HTML content of the email body.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        if not all([receiver_email, subject, html_body]):
            print("Error: Missing one or more required arguments ( receiver_email, subject, html_body).")
            return False

        try:
            message = MIMEMultipart("alternative")
            message["From"] = settings.email.SENDER
            message["To"] = receiver_email
            message["Subject"] = subject

            html_part = MIMEText(html_body, "html")
            message.attach(html_part)

            with smtplib.SMTP(settings.email.HOST, settings.email.PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(settings.email.USER, settings.secrets.SMTP_KEY)
                server.sendmail(settings.email.SENDER, receiver_email, message.as_string())
            return True
        except smtplib.SMTPAuthenticationError:
            print("SMTP Authentication Error: The username or password you entered is incorrect. If using Gmail, ensure 'Less secure app access' is ON or use an App Password.")
            return False
        except smtplib.SMTPServerDisconnected:
            print("SMTP Server Disconnected: Could not connect to the server. Check the server address and port.")
            return False
        except smtplib.SMTPConnectError:
            print(f"SMTP Connect Error: Failed to connect to the server at {settings.email.HOST}:{settings.email.PORT}.")
            return False
        except smtplib.SMTPException as e:
            print(f"An SMTP error occurred: {e}")
            return False
        except ConnectionRefusedError:
            print(f"Connection Refused: Ensure the SMTP server ({settings.email.HOST}:{settings.email.PORT}) is correct and reachable.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False