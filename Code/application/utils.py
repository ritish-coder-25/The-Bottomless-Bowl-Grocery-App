from application.models import User
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


SMPTP_SERVER_HOST = "localhost"
SMPTP_SERVER_PORT = 1025
SENDER_ADDRESS = "21f3000959@ds.study.iitm.ac.in"
SENDER_PASSWORD = "gaWHkzjp"

def send_email(to_address, subject, message, content="text", attachment_file=None):
	user = User.query.filter_by(email=to_address).first()

	if user:
		msg = MIMEMultipart()
		msg['From'] = SENDER_ADDRESS
		msg['To'] = to_address
		msg['Subject'] = subject

		if content == "html":
			msg.attach(MIMEText(message, "html"))
		else:
			msg.attach(MIMEText(message, "plain"))

		if attachment_file:
			attachment = MIMEApplication(attachment_file.getValue(), Name="Monthly_Activity_Report.pdf")
			attachment['Content-Disposition'] = f'attachment; filename="Monthly_Activity_Report.pdf"'
			msg.attach(attachment)

		s = smtplib.SMTP(host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
		s.login(SENDER_ADDRESS, SENDER_PASSWORD)
		s.send_message(msg)
		s.quit()
		return True
	else:
		return False

def send_email_monthly(to_address, subject, message, content="text", attachment_file=None):
    user = User.query.filter_by(email=to_address).first()

    if user:
        msg = MIMEMultipart()
        msg['From'] = SENDER_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = subject

        if content == "html":
            msg.attach(MIMEText(message, "html"))
        else:
            msg.attach(MIMEText(message, "plain"))

        if attachment_file:
            # Directly use the bytes object
            attachment = MIMEApplication(attachment_file, Name="Monthly_Activity_Report.pdf")
            attachment['Content-Disposition'] = f'attachment; filename="Monthly_Activity_Report.pdf"'
            msg.attach(attachment)

        s = smtplib.SMTP(host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
        s.login(SENDER_ADDRESS, SENDER_PASSWORD)
        s.send_message(msg)
        s.quit()
        return True
    else:
        return False

