import os

from django.conf import settings
from sgw.core import SendGrid

os.environ['DJANGO_SETTINGS_MODULE'] = 'base.settings'

email_handler = SendGrid(settings.SENDGRID_APIKEY,
                         settings.SENDGRID_FROM_EMAIL,
                         settings.SENDGRID_FROM_NAME)


def send_confirmation_account_email(name, url, email):
    email_handler.send(to=email,
                       subject='Confirmación de cuenta',
                       msg='<p>Hola {0},</p>'
                       '<p>Pulsa este enlace para confirmar tu cuenta:<br>'
                       "<a href='{1}'>{1}</a></p>".format(name, url),
                       html=True)


def send_remind_credentials_email(username, url, email):
    email_handler.send(to=email,
                       subject='Recordar credenciales',
                       msg='<p>Hola,</p>'
                       '<p>Tu nombre de usuario es: <strong>{0}</strong></p>'
                       '<p>Pulsa este enlace para resetear tu contraseña:<br>'
                       "<a href='{1}'>{1}</a></p>".format(username, url),
                       html=True)


def send_new_video_email(video_name, url, emails):
    for email in emails:
        email_handler.send(
            to=email,
            subject='Nuevo vídeo en Susikiu',
            msg='<p>Hola,</p>'
            '<p>Ya puedes disfrutar de <strong>{0}</strong>:<br>'
            "<a href='{1}'>{1}</a></p>".format(video_name, url),
            html=True)
