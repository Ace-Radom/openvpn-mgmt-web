import os

from jinja2 import Environment, FileSystemLoader

from app import config
from app.helpers import requests_helper

templates = Environment(
    loader=FileSystemLoader(
        os.path.join(os.path.split(os.path.realpath(__file__))[0], "templates")
    )
)

def send_email(
    reciever_email_addr: str, subject: str, template_name: str, context: dict
):
    template = templates.get_template(template_name)
    mail_str = template.render(context)
    sender_name = config.config["mailgun"]["sender_name"]
    sender_email_addr = config.config["mailgun"]["sender_email_addr"]
    auth = ("api", config.config["mailgun"]["api_key"])
    data = {
        "from": f"{ sender_name } <{ sender_email_addr }>",
        "to": reciever_email_addr,
        "subject": subject,
        "html": mail_str,
    }
    if len(config.config["mailgun"]["bcc_email_addr"]) != 0:
        data["bcc"] = config.config["mailgun"]["bcc_email_addr"]
    status_code, _ = requests_helper.post(
        config.config["mailgun"]["api_host"],
        endpoint=config.config["mailgun"]["api_endpoint"],
        use_https=True,
        auth=auth,
        data=data,
        requests_send_with_data_param=True
    )
    return status_code == 200
