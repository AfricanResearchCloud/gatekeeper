from smtplib import SMTP, SMTP_SSL
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import markdown

SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = settings.SMTP_PORT
SMTP_TLS = settings.SMTP_TLS
SMTP_USERNAME = settings.SMTP_USERNAME
SMTP_PASSWORD = settings.SMTP_PASSWORD

def sendemail(to_addr, from_addr, textbody, bcc=None):
    smtp = SMTP(SMTP_SERVER, int(SMTP_PORT))
    if SMTP_TLS:
        smtp.starttls()
    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
    msg = MIMEMultipart('alternative')
    msg.attach(MIMEText(textbody, 'plain'))
    msg.attach(MIMEText(markdown.markdown(textbody), 'html'))
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = 'Terms Signed'
    smtp.sendmail(from_addr, [to_addr, bcc], msg.as_string())
    smtp.close()
