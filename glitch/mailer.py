import smtplib
from email.mime.text import MIMEText
from . import apikeys

import sendgrid
import os
from sendgrid.helpers.mail import *

def alert_message(message, subject='Glitch System Message', me=apikeys.system_email, you=apikeys.admin_email):
	sg = sendgrid.SendGridAPIClient(api_key=apikeys.SENDGRID_API_KEY)
	from_email = Email(me)
	to_email = To(you)
	content = Content("text/plain", message)
	mail = Mail(from_email, to_email, subject, content)
	response = sg.client.mail.send.post(request_body=mail.get())
	print(response.status_code)
	print(response.body)
	print(response.headers)
	return True
