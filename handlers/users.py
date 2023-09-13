import datetime
import json
import time

from loader import bot, db, logger, dp
import config
from . import keyboards as kb

from aiogram.filters import CommandStart
from aiogram import F
from aiogram.types import Message
from aiogram import Router, types
from aiogram.fsm.context import FSMContext


router = Router(name="users")


@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user:
        logger.info(f"user with id {message.from_user.id} not found in users db, adding new user...")
        await db.add_user(message.from_user.id)
    else:
        return await open_menu(message, state, edit=False)
    text = f"Приветствую, <b><i>{message.from_user.full_name}</i></b>.\n\n" \
           f"• Бот создан специально для <i>Codemasters Code Cup 2023</i>.\n\n" \
           f"• Код проекта можно посмотреть по ссылке: <i><a href='https://notabug.org'>клик</a></i>.\n\n" \
           f"• Для начала работы с ботом нажмите кнопку <b>«Начать»</b>."
    return await message.answer(text, reply_markup=kb.start_kb, disable_web_page_preview=True)


@router.message(F.text == "/menu")
async def open_menu(message, state: FSMContext, edit: bool = False):
    text = "<b><i>Главное меню.</i></b>\nВыберите, что хотите сделать."
    if edit:
        return await message.edit_text(text, reply_markup=kb.main_kb)
    return await message.answer(text, reply_markup=kb.main_kb)


async def main_callback(query: types.CallbackQuery, state: FSMContext):
    act = query.data.split(':')[-1]
    if act == "menu":
        await query.message.edit_reply_markup(None)
        return await open_menu(query.message, state, edit=False)


@router.callback_query()
async def callback_handler(query: types.CallbackQuery, state: FSMContext):
    module = query.data.split(':')[0]
    if module == "main":
        return await main_callback(query, state)

