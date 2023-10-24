from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

main_kb = [
    [KeyboardButton(text='בדיקות להזמנה'),
     KeyboardButton(text='הזמנה')],
    [KeyboardButton(text='Мой профиль'),
     KeyboardButton(text='Контакты')]
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

catalog = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='גילוי אש', callback_data='גילוי אש')],
    [InlineKeyboardButton(text='כיבוי בגז', callback_data='כיבוי בגז')],
    [InlineKeyboardButton(text='כיבוי באירוסול', callback_data='כיבוי באירוסול')],
    [InlineKeyboardButton(text='אינטגרציה', callback_data='אינטגרציה')]
])
