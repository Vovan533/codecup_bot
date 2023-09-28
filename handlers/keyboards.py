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

search_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="👤 Поиск по ФИО", callback_data="search:name")
    ],
    [
        InlineKeyboardButton(text="🗂 Поиск по проекту", callback_data="search:project")
    ],
    [
        InlineKeyboardButton(text="🗂👨‍💼 Поиск внутри проекта", callback_data="search:project_user")
    ],
    [
        InlineKeyboardButton(text="👨‍💼 Поиск по должности", callback_data="search:position")
    ],
    [
        InlineKeyboardButton(text="🕓 Поиск по времени прихода", callback_data="search:time")
    ],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="main:back")
    ]
])

search_proj_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📋 Списки по проектам", callback_data="search:project")
        ]
])

search_pos_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📋 Списки по должностям", callback_data="search:position_list")
        ]
])


async def create_project_search_kb(projects: dict) -> InlineKeyboardMarkup | None:
    if not projects:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔙 В меню поиска", callback_data="main:search")
    ]] + [
        [
            InlineKeyboardButton(text=project, callback_data=f"search:s_project:{project}")
        ] for project in projects
    ])


async def create_position_search_kb(positions: dict) -> InlineKeyboardMarkup | None:
    if not positions:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔙 В меню поиска", callback_data="main:search")
    ]] + [
        [
            InlineKeyboardButton(text=pos, callback_data=f"search:s_pos:{pos}")
        ] for pos in positions
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

async def create_personal_list_kb(personal: list, search: bool = False) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="🔙 Главное меню", callback_data="main:back")
        ],
    ]
    if not search:
        kb.append([
            InlineKeyboardButton(text="🗂 Открыть списки по проектам", callback_data="search:project")
        ])
        kb.append([
            InlineKeyboardButton(text="👨‍💼 Открыть списки по должности", callback_data="search:position_list")
        ])
    if personal:
        for pers in personal:
            kb.append([InlineKeyboardButton(text=pers['full_name'].title(),
                                            callback_data=f'pers:show:{pers["personal_id"]}')])
    return InlineKeyboardMarkup(inline_keyboard=kb)


async def create_personal_kb(personal_id: int, role) -> InlineKeyboardMarkup | None:
    if personal_id == -1:
        return None
    kb = [
        [
            InlineKeyboardButton(text="🔙 Список всех сотрудников", callback_data=f"pers:back:{personal_id}")
        ]
    ]
    if role == "admin":
        kb.append([
            InlineKeyboardButton(text="Редактировать", callback_data=f'pers:edit:{personal_id}')
        ])
        kb.append([
            InlineKeyboardButton(text="Удалить", callback_data=f'pers:del:{personal_id}')
        ])
    return InlineKeyboardMarkup(inline_keyboard=kb)
