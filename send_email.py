import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from aiogram.types import Message
from dotenv import load_dotenv
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

email_to = os.getenv('SMTP_reciever')
app_password = os.getenv('SMTP_APP_PASSWORD')
sender_email = os.getenv('SMTP_sender')
downloads_directory = os.getenv('directory')


async def download_document(message: Message):
    """
    Download a document from a Telegram message.

    Parameters:
        message (Message): The Telegram message containing the document.

    Returns:
        str: The local path where the document has been downloaded.
    """
    from main import bot as main_bot
    file_info = await main_bot.get_file(message.document.file_id, request_timeout=60)
    file_path_on_telegram = file_info.file_path
    # file_name = os.path.basename(file_path_on_telegram)
    file_name = message.document.file_name
    destination_path = os.path.join(downloads_directory, file_name)

    await main_bot.download_file(file_path_on_telegram, destination_path)
    return destination_path


async def send_email_with_attachment(client_data=None, bdika_gilui_data=None, attachment_path=None):
    subject = 'הזמנת בדיקה כולל מסמך'
    body = 'הזמנה זו כוללת מסמך מצורף'
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_to
    msg['Subject'] = subject
    try:
        # Форматирование данных клиента и BdikaGilui для включения в тело электронной почты
        field_names = {
            'id': 'מספר הזמנה',
            'client_name': 'שם לקוח',
            'shem_hevra': 'שם החברה',
            'telefon': 'מספר טלפון',
            'makom_shembg': 'שם מקום הבדיקה',
            'makom_ktovetbg': 'כתובת מקום הבדיקה',
            'makom_yehudbg': 'ייעוד המבנה',
            'kamut_galaimbg': 'כמות גלאים',
            'makom_locationbg': 'כתובת מקום הבדיקה',
            'check_datebg': 'תאריך הבדיקה',
            'document_namebg': 'שם מסמך מצורף',
        }

        client_details = '\n'.join(f"{field_names.get(key, key)}: {value}" for key, value in client_data.items())
        bdika_gilui_details = '\n'.join(
            f"{field_names.get(key, key)}: {value}" for key, value in bdika_gilui_data[0].items())

        # body_with_details =
        # f"{body}\n\nClient Details:\n{client_details}\n\nBdikaGilui Details:\n{bdika_gilui_details}"
        client_details_html = client_details.replace('\n', '<br>')
        bdika_gilui_details_html = bdika_gilui_details.replace('\n', '<br>')

        body_with_details = f"""<html>
                <head></head>
                <body dir='rtl'>
                {body}
                <br><br>
                <b>פרטי לקוח: </b><br>
                {client_details_html}
                <br><br>
                <b>פרטי בדיקת גילוי:</b><br>
                {bdika_gilui_details_html}
                </body>
                </html>"""

        msg.attach(MIMEText(body_with_details, 'html'))

        if attachment_path:
            with open(attachment_path, "rb") as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=str(attachment_path))
                msg.attach(attach)
            # Отправка письма через сервер Gmail
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, app_password)
            server.sendmail(sender_email, email_to, msg.as_string())
            server.quit()
        else:
            print(f"Attachment file {attachment_path} does not exist.")
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        logger.error(traceback.format_exc())


async def send_email_without_attachment(client_data=None, bdika_gilui_data=None):
    subject = 'הזמנת בדיקה'
    body = 'ללא מסמך'
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_to
    msg['Subject'] = subject

    try:
        field_names = {
            'id': 'מספר הזמנה',
            'client_name': 'שם לקוח',
            'shem_hevra': 'שם החברה',
            'telefon': 'מספר טלפון',
            'makom_shembg': 'שם מקום הבדיקה',
            'makom_ktovetbg': 'כתובת מקום הבדיקה',
            'makom_yehudbg': 'ייעוד המבנה',
            'kamut_galaimbg': 'כמות גלאים',
            'makom_locationbg': 'כתובת מקום הבדיקה',
            'check_datebg': 'תאריך הבדיקה',
        }

        client_details = '\n'.join(f"{field_names.get(key, key)}: {value}" for key, value in client_data.items())
        bdika_gilui_details = '\n'.join(
            f"{field_names.get(key, key)}: {value}" for key, value in bdika_gilui_data[0].items()
        )

        client_details_html = client_details.replace('\n', '<br>')
        bdika_gilui_details_html = bdika_gilui_details.replace('\n', '<br>')

        body_with_details = f"""<html>
        <head></head>
        <body dir='rtl'>
        {subject}
        {body}
        <br><br>
        <b>פרטי לקוח: </b><br>
        {client_details_html}
        <br><br>
        <b>פרטי בדיקת גילוי:</b><br>
        {bdika_gilui_details_html}
        </body>
        </html>"""

        msg.attach(MIMEText(body_with_details, 'html'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        server.sendmail(sender_email, email_to, msg.as_string())
        server.quit()
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        logging.error(traceback.format_exc())
