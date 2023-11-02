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
    [KeyboardButton(text='שלח הזמנה'),
     KeyboardButton(text='שלח הזמנה')]
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

catalog = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='גילוי אש', callback_data='gilui_esh')]

])

order = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='מעבר לשליחת הזמנה כולל מסמך מצורף לפני', callback_data='to_order')]
])
order_no_doc = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='מעבר לשליחת הזמנה בלי מסמך', callback_data='to_order_no_doc')]
])
