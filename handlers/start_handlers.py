from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from handlers.states import ClientForm, BdikaGiluiForm
from aiogram.fsm.context import FSMContext
from db.db_config import AsyncSessionLocal
from db.models import Client
import kb.keyboards as kb
import logging
import re

start_router = Router()


# Handle the "/start" command to initiate the form filling process
@start_router.message(F.text == '/start')
async def cmd_start(message: Message, state: FSMContext):
    await message.answer('ברוכים הבאים לאייקון! מעבדות כדי להתחיל הזמנה יש לרשום פרטי לקוח.')
    await state.set_state(ClientForm.Client_name)
    await message.reply("נא כתוב שם הלקוח:")


# Handle the "/start" command to initiate the form filling process
@start_router.message(F.text == 'start')
async def cmd_start(message: Message, state: FSMContext):
    await message.answer('ברוכים הבאים לאייקון מעבדות! כדי להתחיל הזמנה יש לרשום פרטי לקוח.')
    await state.set_state(ClientForm.Client_name)
    await message.reply("נא כתוב שם הלקוח:")


# Handle the client's name input
@start_router.message(ClientForm.Client_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(client_name=message.text)
    await state.set_state(ClientForm.Shem_hevra)
    await message.reply("נא כתוב שם החברה:")


# Handle the company name input
@start_router.message(ClientForm.Shem_hevra)
async def process_shem_hevra(message: Message, state: FSMContext):
    await state.update_data(shem_hevra=message.text)
    await state.set_state(ClientForm.Telefon)
    await message.reply("נא כתוב מספר טלפון:")


# Handle the phone number input
@start_router.message(ClientForm.Telefon)
async def process_telefon(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone_number = message.text.strip()

    # Проверка номера телефона с помощью регулярного выражения
    if not re.fullmatch(r'\d{10}', phone_number):
        await message.reply("רישום מספר טלפון אינו תקין.נא רשום כדוגמא '0548330000'")
        return

    await state.update_data(telefon=int(phone_number))  # Сохранение номера телефона в состоянии
    await message.reply("שומר מידע")
    async with AsyncSessionLocal() as session:
        try:
            data = await state.get_data()  # Extract saved data

            # Create a new Client object and fill it with data
            new_client = Client(
                user_id=user_id,
                client_name=data['client_name'],
                shem_hevra=data['shem_hevra'],
                telefon=(data['telefon'])
            )

            # Add the new object to the session and save it to the database
            session.add(new_client)
            await session.commit()
            await message.answer('נא בחירתך סוג בדיקה להזמנה:', reply_markup=kb.catalog)
            await state.update_data(client_id=new_client.id)
            await state.set_state(ClientForm.ChooseTest)  # Move to the next state
        except Exception as e:
            await session.rollback()  # Rollback the transaction in case of an error
            await message.reply(f" טעות בשמירת מידע : {e}")
        finally:
            await session.close()


# Handler for choosing 'gilui_esh' test type
@start_router.callback_query(F.data == 'gilui_esh')
async def process_gilui_esh_choice(callback: CallbackQuery, state: FSMContext):
    logging.info(f"Received callback data: {callback.data}")  # Log the received callback data
    await state.update_data(chosen_test=callback.data)
    logging.info(f"Current state: {await state.get_state()}")
    logging.info("Setting state to BdikaGiluiForm.MakomShemBG")  # Log the state transition
    await state.set_state(BdikaGiluiForm.MakomShemBG)
    await callback.message.answer(f'נא כתוב שם מקום הבדיקה:')
