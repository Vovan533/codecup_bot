from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, CallbackData
from loader import db


start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Начать", callback_data="main:menu")
    ],
])

today_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Сегодня", callback_data="today")
    ],
])

confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Подтвердить создание", callback_data="confirm")
    ],
    [
        InlineKeyboardButton(text="Отменить", callback_data="cancel")
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

cancel_b_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Отменить", callback_data="cancel_b")
    ]
])

edit_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Изменить ФИО", callback_data="name")
    ],
    [
        InlineKeyboardButton(text="Изменить должность", callback_data="position")
    ],
    [
        InlineKeyboardButton(text="Изменить проект", callback_data="project")
    ],
    [
        InlineKeyboardButton(text="Изменить аватарку", callback_data="avatar")
    ],
    [
        InlineKeyboardButton(text="Изменить дату прихода", callback_data="time_join")
    ],
    [
        InlineKeyboardButton(text="Завершить изменения", callback_data="confirm")
    ],
    [
        InlineKeyboardButton(text="Отменить", callback_data="cancel")
    ],
])


# Список выводит до 99 сотрудников, возможна последующая доработка, до вывода любого кол-ва через создание страниц.

async def create_personal_list_kb(personal: list) -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text="🔙 Назад", callback_data="main:back")]]
    if personal:
        for pers in personal:
            kb.append([InlineKeyboardButton(text=pers['full_name'].title(),
                                            callback_data=f'pers:show:{pers["personal_id"]}')])
    return InlineKeyboardMarkup(inline_keyboard=kb)


async def create_personal_kb(personal_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Редактировать", callback_data=f'pers:edit:{personal_id}')
        ],
        [
            InlineKeyboardButton(text="Удалить", callback_data=f'pers:del:{personal_id}')
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data=f"pers:back:{personal_id}")
        ]
    ])
