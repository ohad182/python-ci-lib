import socket
import platform
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DEFAULT_SENDER_EMAIL = None
DEFAULT_SENDER_ALIAS = None
SMTP_HOST = None
SMTP_PORT = 0


def get_env_info():
    host = socket.gethostname()
    python_version = platform.python_version()
    os_info = platform.platform()
    return """Host: {}
    python: {}
    os: {}
    """.format(host, python_version, os_info)


def send(to, subject, body, sender_email=DEFAULT_SENDER_EMAIL, sender_alias=DEFAULT_SENDER_ALIAS, add_env_info=False):
    if add_env_info:
        body = "{}\n\n\n{}".format(body, get_env_info())

    sender = sender_email if sender_alias is None else "{} <{}>".format(sender_alias, sender_email)

    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = to

    part1 = MIMEText(body, 'plain')
    part2 = MIMEText(body, 'html')
    message.attach(part1)
    message.attach(part2)

    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)

    # TODO: logging.debug("Sending mail '{}' to {}".format(subject, to))
    smtp.sendmail(sender, [to], message.as_string())
    smtp.quit()
