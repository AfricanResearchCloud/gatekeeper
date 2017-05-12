from smtplib import SMTP, SMTP_SSL
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from os import walk, path
import markdown
import logging

SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = settings.SMTP_PORT
SMTP_TLS = settings.SMTP_TLS
SMTP_USERNAME = settings.SMTP_USERNAME
SMTP_PASSWORD = settings.SMTP_PASSWORD
EMAIL_IMAGE_PATH =  settings.CUSTOM_SETTINGS_PATH + "/email/images/"
LOG = logging.getLogger(__name__)

def sendemail(to_addr, from_addr, subject, textbody, bcc=None):
    smtp = SMTP(SMTP_SERVER, int(SMTP_PORT))
    if SMTP_TLS:
        smtp.starttls()
    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
    msg = MIMEMultipart('alternative')
    for filename in next(walk(EMAIL_IMAGE_PATH))[2]:
        fp = open(EMAIL_IMAGE_PATH + filename, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<' + path.splitext(filename)[0] + '>')
        msg.attach(msgImage)
        LOG.info("attaching %s with Content-ID %s" % (filename, path.splitext(filename)[0]))
    msg.attach(MIMEText(textbody, 'plain'))
    msg.attach(MIMEText(markdown.markdown(textbody), 'html'))
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addr)
    msg['Subject'] = subject
    LOG.info("Sending Email to %s with subject %s" % (', '.join(to_addr), subject))
    smtp.sendmail(from_addr, list(to_addr) + list(bcc) if bcc else list(to_addr), msg.as_string())
    smtp.close()
