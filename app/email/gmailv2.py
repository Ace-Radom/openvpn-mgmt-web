import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader

from app import config

templates = Environment(
    loader=FileSystemLoader(
        os.path.join(os.path.split(os.path.realpath(__file__))[0], "templates")
    )
)

def create_email(
    reciever_email_addr: str, subject: str, template_name: str, context: dict
):
    template = templates.get_template(template_name)
    mail = MIMEText(template.render(context), "html", "utf-8")
    mail["from"] = config.config["gmail"]["sender_email_addr"]
    mail["to"] = reciever_email_addr
    mail["subject"] = subject

    return mail

def send_email(
    reciever_email_addr: str, subject: str, template_name: str, context: dict
):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(config.config["gmail"]["sender_email_addr"], config.config["gmail"]["app_pswd"])
            server.send_message(create_email(reciever_email_addr, subject, template_name, context))
        return True
    except Exception as e:
        print(e)
        return False
