# Import smtplib for the actual sending function
import smtplib
from email.mime.text import MIMEText
import apikeys

def AlertMessage(message, subject='Glitch System Message', me=apikeys.system_email, you=apikeys.admin_email):
	msg = MIMEText(message)

	msg['Subject'] = subject
	msg['From'] = me
	msg['To'] = you

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	s = smtplib.SMTP('localhost')
	s.sendmail(me, [you], msg.as_string())
	s.quit()
	
a_message = 'There is someting I need to tell you.'
AlertMessage(a_message)