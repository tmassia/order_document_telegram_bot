import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv


# load_dotenv()

# sender = os.getenv('SMTP_sender')


async def send_email_with_attachment(email_to, subject, body, attachment_path, password, sender_email):
    # sender_email = sender

    # Создание экземпляра MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_to
    msg['Subject'] = subject

    # Текст письма
    msg.attach(MIMEText(body, 'plain'))

    # Вложение
    with open(attachment_path, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename=str(attachment_path))
        msg.attach(attach)

    # Отправка письма через сервер Gmail
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, password)
    server.sendmail(sender_email, email_to, msg.as_string())
    server.quit()
