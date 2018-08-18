from fabric.contrib import django
django.settings_module('base.settings')
from django.conf import settings
_ = settings.INSTALLED_APPS  # fabric bug: https://goo.gl/167WlO
from django.core.mail import EmailMultiAlternatives


def send_confirmation_account_email(name, url, email):
    msg = EmailMultiAlternatives(
        subject="Confirmación de cuenta",
        body="<p>Hola {0},</p>"
             "<p>Pulsa este enlace para confirmar tu cuenta:<br>"
             "<a href='{1}'>{1}</a></p>".format(
                name,
                url
             ),
        to=["{}".format(email)]
    )
    msg.content_subtype = "html"
    msg.send()


def send_remind_credentials_email(username, url, email):
    msg = EmailMultiAlternatives(
        subject="Recordar credenciales",
        body="<p>Hola,</p>"
             "<p>Tu nombre de usuario es: <strong>{0}</strong></p>"
             "<p>Pulsa este enlace para resetear tu contraseña:<br>"
             "<a href='{1}'>{1}</a></p>".format(
                username,
                url
             ),
        to=["{}".format(email)]
    )
    msg.content_subtype = "html"
    msg.send()


def send_new_video_email(video_name, url, emails):
    msg = EmailMultiAlternatives(
        subject="Nuevo vídeo en Susikiu",
        body="<p>Hola,</p>"
             "<p>Ya puedes disfrutar de <strong>{0}</strong>:<br>"
             "<a href='{1}'>{1}</a></p>".format(
                video_name,
                url
             ),
        bcc=emails
    )
    msg.content_subtype = "html"
    msg.send()
