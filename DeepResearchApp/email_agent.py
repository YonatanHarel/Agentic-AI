from ast import Dict
import os
from agents import Agent, function_tool
import sendgrid

from email_test import email_content

SENDER_EMAIL = os.environ.get("SENDER_EMAIL", None)
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", None)


@function_tool
def send_email(subject: str, html_body: str):
    """ Send out an email with the given subject and HTML body """
    if SENDER_EMAIL is None or RECIPIENT_EMAIL is None:
        return "Error"
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = sendgrid.Email(SENDER_EMAIL)
    to_email = sendgrid.To(RECIPIENT_EMAIL)
    content = sendgrid.Content("text/html", html_body)
    mail = sendgrid.Mail(from_email, to_email, subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return  "success"

INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini"
)

# if __name__ == '__main__':
#     send_email(email_content["subject"],email_content["html_body"])