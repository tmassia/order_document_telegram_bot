import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from aiogram.types import Message
from dotenv import load_dotenv
import logging
import traceback
import requests
from b2sdk.v1 import InMemoryAccountInfo, B2Api
from io import BytesIO

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
load_dotenv()
application_key_id = os.getenv('b2_app_key_id')  # получено из Backblaze B2
application_key = os.getenv('b2_app_key')  # получено из Backblaze B2
bucket_name = os.getenv('b2_bucket_name')
info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", application_key_id, application_key)
bucket = b2_api.get_bucket_by_name(bucket_name)

email_to = os.getenv('SMTP_reciever')
app_password = os.getenv('SMTP_APP_PASSWORD')
sender_email = os.getenv('SMTP_sender')
# downloads_directory = os.getenv('directory')


async def download_document(message: Message):
    from main import bot as main_bot
    file_info = await main_bot.get_file(message.document.file_id, request_timeout=120)
    file_path_on_telegram = file_info.file_path
    file_name = message.document.file_name  # Используем имя файла из сообщения

    # Загрузка файла с Telegram
    byte_data = await main_bot.download_file(file_path_on_telegram)
    # Загрузка файла в Backblaze B2
    byte_data = byte_data.read()
    bucket.upload_bytes(byte_data, file_name)
    # Получение URL для скачивания файла
    download_url = b2_api.get_download_url_for_file_name(bucket_name, file_name)
    logger.debug(f"Returning from download_document: URL: {download_url}, File Name: {file_name}")
    logger.debug(f"Download URL: {download_url}, File Name: {file_name}")
    return download_url, file_name


async def send_email_with_attachment(client_data=None, bdika_gilui_data=None, attachment_url=None,
                                     attachment_filename=None):
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
        if attachment_url:
            # Скачиваем файл в оперативную память
            response = requests.get(attachment_url)
            byte_stream = BytesIO(response.content)
            attach = MIMEApplication(byte_stream.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename=attachment_filename)
            msg.attach(attach)
            byte_stream.close()
            # Отправка письма через сервер Gmail
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, app_password)
            server.sendmail(sender_email, email_to, msg.as_string())
            server.quit()
        else:
            print(f"Attachment file {attachment_url} does not exist.")
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
