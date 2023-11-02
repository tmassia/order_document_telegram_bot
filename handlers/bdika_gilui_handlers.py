from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import types
from aiogram import F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.states import BdikaGiluiForm
from send_email import download_document, send_email_with_attachment, send_email_without_attachment
from kb import keyboards as kb
from db.db_config import AsyncSessionLocal
from db.models import BdikaGilui, Client
import logging
from sqlalchemy import select

import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
bdika_gilui_router = Router()

# Create a keyboard with "Yes" and "No" buttons
markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="כן", callback_data="upload_document")],
    [InlineKeyboardButton(text="לא", callback_data="no_upload")]
])


# Handler for the "MakomShemBG" state
@bdika_gilui_router.message(BdikaGiluiForm.MakomShemBG)
async def process_makom_shembg(message: Message, state: FSMContext):
    await state.update_data(makom_shembg=message.text)
    await state.set_state(BdikaGiluiForm.MakomYehudBG)
    await message.reply("מה ייעוד המבנה :")


# Handler for the "MakomYehudBG" state
@bdika_gilui_router.message(BdikaGiluiForm.MakomYehudBG)
async def process_makom_yehudbg(message: Message, state: FSMContext):
    await state.update_data(makom_yehudbg=message.text)
    await state.set_state(BdikaGiluiForm.MakomKtovetBG)
    await message.reply("מה כתובת מקום הבדיקה:")


# Handler for the "MakomKtovetBG" state
@bdika_gilui_router.message(BdikaGiluiForm.MakomKtovetBG)
async def process_makom_ktovetbg(message: Message, state: FSMContext):
    await state.update_data(makom_ktovetbg=message.text)
    await state.set_state(BdikaGiluiForm.MakomLocationBG)
    await message.reply("שלח לינק מיקום :")


# Handler for the "MakomLocationBG" state
@bdika_gilui_router.message(BdikaGiluiForm.MakomLocationBG)
async def process_makom_locationbg(message: Message, state: FSMContext):
    await state.update_data(makom_locationbg=message.text)
    await state.set_state(BdikaGiluiForm.KamutGalaimBG)
    await message.reply("רשום כמות גלאים :")


# Handler for the "KamutGalaimBG" state
@bdika_gilui_router.message(BdikaGiluiForm.KamutGalaimBG)
async def process_kamut_galaimbgb(message: Message, state: FSMContext):
    await state.update_data(kamut_galaimbg=message.text)
    await state.set_state(BdikaGiluiForm.CheckDateBG)
    await message.reply("תאריך בדיקה נא לכתוב כדוגמא   '01/01/2024' או '01.01.2024':")


# Handler for the "CheckDateBG" state
@bdika_gilui_router.message(BdikaGiluiForm.CheckDateBG)
async def process_check_datebg(message: types.Message, state: FSMContext):
    await state.update_data(check_datebg=message.text)
    await message.reply("שומר מידע")
    async with AsyncSessionLocal() as session:
        try:
            data = await state.get_data()
            client_id = data.get('client_id')  # Extract client_id from state
            new_bdikat_gilui = BdikaGilui(
                id_order=client_id,
                makom_shembg=data['makom_shembg'],
                makom_yehudbg=data['makom_yehudbg'],
                makom_ktovetbg=data['makom_ktovetbg'],
                makom_locationbg=data['makom_locationbg'],
                kamut_galaimbg=int(data['kamut_galaimbg']),
                check_datebg=data['check_datebg']
            )

            # Add the new object to the session and save it to the database
            session.add(new_bdikat_gilui)
            await session.commit()
            await state.update_data(bdika_gilui_id=new_bdikat_gilui.id)
            await message.reply("רוצה מסמך לצרף?", reply_markup=markup)
        except Exception as e:
            await session.rollback()
            await message.reply(f"טעות בשמירת מידע: {e}")
        finally:
            await session.close()


# Callback handler for choosing to upload a document
@bdika_gilui_router.callback_query(F.data == "upload_document")
async def process_upload_document(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BdikaGiluiForm.FileUploadBG)
    await callback.message.reply("נא לעלות את המסמכך.")


# Handler for the "FileUploadBG" state
@bdika_gilui_router.message(BdikaGiluiForm.FileUploadBG)
async def process_file_upload(message: Message, state: FSMContext):
    destination_path, file_name = await download_document(message)
    try:
        await state.update_data(file_url=destination_path, file_name=file_name)
    except Exception as e:
        await message.reply(f"טעות בשמירת מידע: {e}")
        return  # Возвращаемся из функции в случае ошибки
    # Обновляем запись в базе данных
    async with AsyncSessionLocal() as session:
        try:
            data = await state.get_data()

            bdika_gilui_id = data.get('bdika_gilui_id')
            # Создаем объект запроса и фильтруем его по ID
            bdika_gilui = await session.execute(select(BdikaGilui).filter_by(id=bdika_gilui_id))
            bdika_gilui = bdika_gilui.scalar_one_or_none()
            if bdika_gilui:
                bdika_gilui.document_namebg = file_name
                bdika_gilui.file_uploadbg = destination_path
                await session.commit()
                await ask_for_next_step(message)
            else:
                await message.reply("טעות :רישום לא נמצא בDB")
        except Exception as e:
            await session.rollback()
            await message.reply(f"טעות בשמירת מידע: {e}")
        finally:
            await session.close()


# Function to ask the user for the next step

async def ask_for_next_step(message: Message):
    await message.reply("מה עושים עכשיו?", reply_markup=kb.order)


# Callback handler for proceeding to the order with document attachment
@bdika_gilui_router.callback_query(F.data == "to_order")
async def process_proceed_to_order(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        try:
            data = await state.get_data()
            client_id = data.get('client_id')  # Используем правильный ключ
            print(f"Debug: client_id = {client_id}")

            if client_id is None:
                await callback.message.answer("טעות: client_id not found")
                return

            client_data = await session.execute(select(Client).filter_by(id=client_id))
            client_data = client_data.scalar_one_or_none()
            # Извлекаем все поля
            all_client_data = {column.name: getattr(client_data, column.name) for column in Client.__table__.columns}

            bdika_gilui_data = await session.execute(select(BdikaGilui).filter_by(id_order=client_id))
            bdika_gilui_data = bdika_gilui_data.scalars().all()
            all_bdika_gilui_data = [
                {column.name: getattr(record, column.name) for column in BdikaGilui.__table__.columns} for record in
                bdika_gilui_data]

            # Оставляем только нужные поля
            required_client_fields = ['id', 'client_name', 'shem_hevra', 'telefon']
            required_bdika_gilui_fields = ['id', 'makom_shembg', 'makom_yehudbg', 'makom_ktovetbg', 'kamut_galaimbg',
                                           'makom_locationbg',
                                           'check_datebg', 'document_namebg']

            filtered_client_data = {key: all_client_data[key] for key in required_client_fields}
            filtered_bdika_gilui_data = [{key: record[key] for key in required_bdika_gilui_fields} for record in
                                         all_bdika_gilui_data]

            if not filtered_client_data or not filtered_bdika_gilui_data:
                await callback.message.answer("טעות מאגר מידע:")
                return
            try:
                # file_path = data.get('file_path')
                file_path = data.get('file_url')
                file_name = bdika_gilui_data[0].document_namebg
                if not file_path:
                    await callback.message.answer("Error: file_path is missing or None")
                    return
                await send_email_with_attachment(client_data=filtered_client_data,
                                                 bdika_gilui_data=filtered_bdika_gilui_data,
                                                 attachment_url=file_path, attachment_filename=file_name)
                await callback.message.answer("הזמנה נשלחה בהצלחה!=)")
            except Exception as e:
                await callback.message.answer(f"טעות בשליחת דואל: {e}")
                logger.error(f"Exception occurred: {e}")
                logger.error(traceback.format_exc())
            finally:
                await session.close()
                await callback.message.answer("session.close")
        except Exception as e:
            await callback.message.answer(f"טעות בשליחת דואל: {e}")
            logger.error(f"Exception occurred: {e}")
            logger.error(traceback.format_exc())
        finally:
            await session.close()


# Callback handler for choosing not to upload a document
@bdika_gilui_router.callback_query(F.data == "no_upload")
async def process_no_upload_document(callback: types.CallbackQuery):
    await ask_for_next_step_no_doc(callback.message)


async def ask_for_next_step_no_doc(message: Message):
    await message.reply("ממשיכים?", reply_markup=kb.order_no_doc)


# Callback handler for proceeding to the order no_doc
@bdika_gilui_router.callback_query(F.data == "to_order_no_doc")
async def process_proceed_to_order(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        try:
            data = await state.get_data()
            client_id = data.get('client_id')  # Используем правильный ключ
            print(f"Debug: client_id = {client_id}")

            if client_id is None:
                await callback.message.answer("טעות: client_id not found.")
                return

            client_data = await session.execute(select(Client).filter_by(id=client_id))
            client_data = client_data.scalar_one_or_none()
            # Извлекаем все поля
            all_client_data = {column.name: getattr(client_data, column.name) for column in Client.__table__.columns}

            bdika_gilui_data = await session.execute(select(BdikaGilui).filter_by(id_order=client_id))
            bdika_gilui_data = bdika_gilui_data.scalars().all()
            all_bdika_gilui_data = [
                {column.name: getattr(record, column.name) for column in BdikaGilui.__table__.columns} for record in
                bdika_gilui_data]

            # Оставляем только нужные поля
            required_client_fields = ['id', 'client_name', 'shem_hevra', 'telefon']
            required_bdika_gilui_fields = ['id', 'makom_shembg', 'makom_yehudbg', 'makom_ktovetbg', 'kamut_galaimbg',
                                           'makom_locationbg',
                                           'check_datebg']

            filtered_client_data = {key: all_client_data[key] for key in required_client_fields}
            filtered_bdika_gilui_data = [{key: record[key] for key in required_bdika_gilui_fields} for record in
                                         all_bdika_gilui_data]

            if not filtered_client_data or not filtered_bdika_gilui_data:
                await callback.message.answer("טעות מאגר מידע:")
                return

            await send_email_without_attachment(client_data=filtered_client_data,
                                                bdika_gilui_data=filtered_bdika_gilui_data
                                                )
            await callback.message.answer("הזמנה נשלחה בהצלחה!=)")
        except Exception as e:
            await callback.message.answer(f"טעות בשליחת דואל:{e}")
            logger.error(f"Exception occurred: {e}")
            logger.error(traceback.format_exc())
        finally:
            await session.close()
