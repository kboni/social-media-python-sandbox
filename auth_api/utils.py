import smtplib
from email.message import EmailMessage
import redis
from flask_init import app


class Redis():
    @staticmethod
    def get_connection():
        return redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=0)


class Mail():
    @staticmethod
    def build_message(
            subject: str, message_content: str, send_to: str,
            sent_from: str = app.config['DEFAULT_MAIL_FROM']) -> EmailMessage:

        email_message = EmailMessage()
        email_message['Subject'] = subject
        email_message['From'] = sent_from
        email_message['To'] = send_to
        email_message.set_content(message_content)

        return email_message

    @staticmethod
    def send(
            message: str, smtp_host: str = app.config['SMTP_HOST'],
            smtp_port: str = app.config['SMTP_PORT']) -> bool:
        try:
            with smtplib.SMTP(host=smtp_host, port=smtp_port) as smtp:
                smtp.send_message(message)
        except smtplib.SMTPException as exception:
            app.logger.error(f'Error while sending e-mail: {exception}')
            return False

        return True
