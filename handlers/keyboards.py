from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, CallbackData
from loader import db


start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Начать", callback_data="main:menu")
    ],
])

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📋 Список сотрудников", callback_data="main:list")
    ],
    [
        InlineKeyboardButton(text="🔎 Поиск сотрудника", callback_data="main:search")
    ],
    [
        InlineKeyboardButton(text="➕ Добавить сотрудника", callback_data="main:add")
    ],
])
