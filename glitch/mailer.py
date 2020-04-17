import smtplib
from email.mime.text import MIMEText
from . import apikeys

def alert_message(message, subject='Glitch System Message', me=apikeys.system_email, you=apikeys.admin_email):
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['From'] = me
	msg['To'] = you
	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	try:
		s = smtplib.SMTP(apikeys.SMTP_SERVER_PORT)
		if apikeys.SMTP_USERNAME:
			s.ehlo()
			s.starttls()
			s.login(apikeys.SMTP_USERNAME, apikeys.SMTP_PASSWORD)
		s.sendmail(me, [you], msg.as_string())
		s.quit()
	except smtplib.SMTPAuthenticationError:
		return False;
