# utils.py

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from online_store.settings import EMAIL_HOST_USER


def send_html_email(subject, message_html, recipient_list):
    email = EmailMessage(
        subject,
        message_html,
        from_email=EMAIL_HOST_USER,
        to=recipient_list,
    )
    email.content_subtype = "html"
    email.send()
