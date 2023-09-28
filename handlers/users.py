import datetime
import json
import time

from loader import bot, db, logger, dp
import config
from . import keyboards as kb

from aiogram.filters import CommandStart
from aiogram import F
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from itertools import permutations


router = Router(name="users")


# === Функции и фильтры ===
async def get_role(user_id: int) -> str:
    user = await db.get_user(user_id)
    if not user:
        logger.error("user not found in db, adding new...")
        await db.add_user(user_id)
        user = await db.get_user(user_id)
    if user['status'] == 'banned':
        return 'banned'
    else:
        return user['role']


async def show_personal(personal: dict, message: types.Message, role: str, edit: bool = False):
    text = f"<b>Фамилия:</b> <i>{personal['last_name'].title()}</i>\n" \
           f"<b>Имя:</b> <i>{personal['first_name'].title()}</i>\n" \
           f"<b>Отчество:</b> <i>{personal['middle_name'].title()}</i>\n\n" \
           f"<b>Должность:</b> <i>{personal['position']}</i>\n" \
           f"<b>Проект:</b> <i>{personal['project']}</i>\n" \
           f"<b>Дата прихода:</b> <i>{datetime.datetime.fromtimestamp(personal['time_join']).strftime('%d.%m.%Y')}</i>\n"
    if 'personal_id' not in personal:
        personal['personal_id'] = -1
    keyboard = await kb.create_personal_kb(personal['personal_id'], role)
    if personal['avatar'] != 'Null':
        with open(personal['avatar'], 'rb') as photo_file:
            file_data = photo_file.read()
            photo = types.BufferedInputFile(file=file_data, filename='personal_photo')
        if edit:
            return await message.answer_photo(photo=photo, caption=text,
                                              reply_markup=keyboard)
        else:
            return await message.answer_photo(photo=photo, caption=text, reply_markup=kb.confirm_kb)
    if edit:
        return await message.answer(text=text, reply_markup=keyboard)
    else:
        return await message.answer(text, reply_markup=kb.confirm_kb)


async def show_personal_list(personal: list, edit: bool, message: Message, search: bool = False):
    if not personal:
        if edit:
            return await message.answer("Список сотрудников пуст.", show_alert=True)
        else:
            return await message.answer("Список сотрудников пуст.")
    text = "<b><i>Список сотрудников.</i></b>" \
           "\nНажмите на ФИО сотрудника, для просмотра информации о нем или редактировании её."
    keyboard = await kb.create_personal_list_kb(personal, search=search)
    if edit:
        return await message.message.edit_text(text, reply_markup=keyboard)
    return await message.answer(text, reply_markup=keyboard)


async def show_no_permission_message(user_request: Message | CallbackQuery) -> None:
    text = "Недостаточно прав для выполнения этого действия."
    if isinstance(user_request, CallbackQuery):
        await user_request.answer(text, show_alert=True)
    else:
        await user_request.answer(text)


async def show_banned_message(user_request: Message | CallbackQuery) -> None:
    text = "Администраторы бота ограничили для Вас это действие."
    if isinstance(user_request, CallbackQuery):
        await user_request.answer(text, show_alert=True)
    else:
        await user_request.answer(text)


class RoleFilter(Filter):
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, user_request: Message | CallbackQuery) -> bool:
        role = await get_role(user_request.from_user.id)
        if role in self.allowed_roles:
            return True
        await show_no_permission_message(user_request)
        return False


class BannedFilter(Filter):
    def __init__(self, is_banned: bool) -> None:
        self.is_banned = is_banned

    async def __call__(self, user_request: Message | CallbackQuery) -> bool:
        role = await get_role(user_request.from_user.id)
        banned = role == "banned"
        if banned and self.is_banned:
            await show_banned_message(user_request)
        return self.is_banned == banned


# === Хендлеры команд от пользователя ===
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
           f"• Код проекта можно посмотреть по ссылке: <i><a href='https://notabug.org/vovan533/codecup_bot'>клик</a></i>.\n\n" \
           f"• Для начала работы с ботом нажмите кнопку <b>«Начать»</b>."
    return await message.answer(text, reply_markup=kb.start_kb, disable_web_page_preview=True)


@router.message(F.text == "/menu")
async def open_menu(message: types.Message, state: FSMContext, edit: bool = False):
    await state.set_state(None)
    text = "<b><i>Главное меню.</i></b>\nВыберите, что хотите сделать."
    if edit:
        return await message.edit_text(text, reply_markup=kb.main_kb)
    return await message.answer(text, reply_markup=kb.main_kb)


@router.message(F.text == "/admin", BannedFilter(False))
async def admin_cmd(message: types.Message, state: FSMContext):
    await state.set_state(None)
    await db.set_user_role(message.from_user.id, "admin")
    return await message.answer("Ваша роль изменена на «Администратор».")


@router.message(F.text == "/user", BannedFilter(False))
async def admin_cmd(message: types.Message, state: FSMContext):
    await state.set_state(None)
    await db.set_user_role(message.from_user.id, "user")
    return await message.answer("Ваша роль изменена на «Пользователь».")


@router.message(F.text == "/list", BannedFilter(False))
async def show_list(message: types.Message | types.CallbackQuery, state: FSMContext, edit: bool = False):
    personal = await db.get_personal()
    await show_personal_list(personal, edit, message)


# === Добавление сотрудника ===
# класс StatesGroup
class AddPersonal(StatesGroup):
    full_name = State()
    position = State()
    project = State()
    avatar = State()
    join_time = State()


# хендлеры на каждый этап создания
@router.message(AddPersonal.full_name, RoleFilter(['admin']), BannedFilter(False))
async def name_handler(message: types.Message, state: FSMContext):
    name_parts = message.text.strip().split()
    if len(name_parts) > 3 or len(name_parts) < 2:
        return await message.answer("Необходимо ввести ФИО через пробел (Отчество при наличии).")
    last_name, first_name = name_parts[0], name_parts[1]
    if len(name_parts) == 3:
        middle_name = name_parts[2]
        full_name = last_name.lower() + ' ' + first_name.lower() + ' ' + middle_name.lower()
    else:
        middle_name = '-'
        full_name = last_name.lower() + ' ' + first_name.lower()
    data = await state.get_data()
    data['first_name'] = first_name
    data['last_name'] = last_name
    data['middle_name'] = middle_name
    data['full_name'] = full_name
    await state.set_data(data)
    await state.set_state(AddPersonal.position)
    return await message.answer(f"ФИО записано.\n<b>Фамилия:</b><i> {last_name}</i>\n<b>Имя:</b><i> {first_name}</i>"
                                f"\n<b>Отчество:</b><i> {middle_name}</i>\n\n"
                                f"Шаг 2 из 5.\nОтправьте должность сотрудника.")


@router.message(AddPersonal.position, RoleFilter(['admin']), BannedFilter(False))
async def position_handler(message: types.Message, state: FSMContext):
    position = message.text.strip()
    data = await state.get_data()
    data['position'] = position
    await state.set_data(data)
    await state.set_state(AddPersonal.project)
    return await message.answer(f"Должность записана (<b>{position}</b>).\n\n"
                                f"Шаг 3 из 5.\nОтправьте название проекта сотрудника.")


@router.message(AddPersonal.project, RoleFilter(['admin']), BannedFilter(False))
async def project_handler(message: types.Message, state: FSMContext):
    project = message.text.strip()
    data = await state.get_data()
    data['project'] = project
    await state.set_data(data)
    await state.set_state(AddPersonal.avatar)
    return await message.answer(f"Проект записан (<b>{project}</b>).\n\nШаг 4 из 5.\n"
                                f"Отправьте фото аватарки сотрудника или введите /skip чтобы пропустить этот этап.")


@router.message(AddPersonal.avatar, F.content_type == 'photo', RoleFilter(['admin']), BannedFilter(False))
async def avatar_handler(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    path = f'data/img/personal/{photo_id}.jpg'
    await bot.download(photo_id, path)
    data = await state.get_data()
    data['avatar'] = path
    await state.set_data(data)
    await state.set_state(AddPersonal.join_time)
    return await message.reply(f"Аватарка сохранена.\n\nШаг 5 из 5.\nОтправьте дату прихода сотрудника в формате "
                               f"дд.мм.гггг или нажмите <b>«Сегодня»</b> для указания сегодняшнего дня.",
                               reply_markup=kb.today_kb)


@router.message(AddPersonal.avatar, RoleFilter(['admin']), BannedFilter(False))
async def avatar_other_handler(message: types.Message, state: FSMContext):
    if message.text.strip() != '/skip':
        return await message.answer("Необходимо отправить аватарку как фото. (отправка файлом не принимается)")
    else:
        data = await state.get_data()
        data['avatar'] = 'Null'
        await state.set_data(data)
        await state.set_state(AddPersonal.join_time)
        return await message.reply(f"Добавление аватарки пропущено."
                                   f"\n\nШаг 5 из 5.\nОтправьте дату прихода сотрудника в формате "
                                   f"дд.мм.гггг или нажмите <b>«Сегодня»</b> для указания сегодняшнего дня.",
                                   reply_markup=kb.today_kb)


@router.callback_query(AddPersonal.join_time, RoleFilter(['admin']), BannedFilter(False))
async def today_handler(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    role = await get_role(query.from_user.id)
    if query.data == "today":
        data['time_join'] = time.time()
        await state.set_data(data)
        await query.message.edit_reply_markup(None)
        await query.message.answer("Дата прихода установлена на сегодня."
                                   "\n\nНачинаю добавление нового сотрудника в базу...")
        return await show_personal(data, query.message, role, edit=False)
    if query.data == "confirm":
        await db.add_personal(data['first_name'], data['last_name'], data['middle_name'], data['full_name'],
                              data['position'], data['project'], data['time_join'], data['avatar'])
        await query.message.edit_reply_markup(None)
        await query.answer("Новый сотрудник добавлен в базу.", show_alert=True)
        return await open_menu(query.message, state, edit=False)
    if query.data == "cancel":
        await query.message.edit_reply_markup(None)
        await query.answer("Добавление сотрудника отменено", show_alert=True)
        return await open_menu(query.message, state, edit=False)


@router.message(AddPersonal.join_time, RoleFilter(['admin']), BannedFilter(False))
async def date_handler(message: types.Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    dt = message.text.strip().split('.')
    if len(dt) != 3 or len(dt[-1]) != 4:
        return await message.answer("Неверный формат даты. Формат: дд.мм.гггг\n* Пример: <i>28.09.2023</i>")
    try:
        date = datetime.datetime(int(dt[2]), int(dt[1]), int(dt[0]))
        timestamp = date.timestamp()
    except Exception as ex:
        return await message.answer(f"Неверный формат даты ({ex})")
    data = await state.get_data()
    data["time_join"] = timestamp
    await state.set_data(data)
    await message.reply("Дата прихода установлена.\n\nНачинаю добавление нового сотрудника в базу...")
    await show_personal(data, message, role, edit=False)


# === Редактирование сотрудника ===
# класс StatesGroup
class EditPersonal(StatesGroup):
    choose = State()
    full_name = State()
    position = State()
    project = State()
    avatar = State()
    join_time = State()


# хендлеры для этапов
@router.message(EditPersonal.full_name, RoleFilter(['admin']), BannedFilter(False))
async def name_handler(message: types.Message, state: FSMContext):
    name_parts = message.text.strip().split()
    if len(name_parts) > 3 or len(name_parts) < 2:
        return await message.answer("Необходимо ввести ФИО через пробел (Отчество при наличии).")
    last_name, first_name = name_parts[0], name_parts[1]
    if len(name_parts) == 3:
        middle_name = name_parts[2]
        full_name = last_name.lower() + ' ' + first_name.lower() + ' ' + middle_name.lower()
    else:
        middle_name = '-'
        full_name = last_name.lower() + ' ' + first_name.lower()
    data = await state.get_data()
    data['first_name'] = first_name
    data['last_name'] = last_name
    data['middle_name'] = middle_name
    data['full_name'] = full_name
    await state.set_data(data)
    await state.set_state(AddPersonal.position)
    await message.answer(f"ФИО изменено.\n<b>Фамилия:</b><i> {last_name}</i>\n<b>Имя:</b><i> {first_name}</i>"
                         f"\n<b>Отчество:</b><i> {middle_name}</i>")
    await state.set_state(EditPersonal.choose)
    return await message.answer("Выберите что хотите сделать.", reply_markup=kb.edit_kb)


@router.message(EditPersonal.position, RoleFilter(['admin']), BannedFilter(False))
async def position_handler(message: types.Message, state: FSMContext):
    position = message.text.strip()
    data = await state.get_data()
    data['position'] = position
    await state.set_data(data)
    await state.set_state(AddPersonal.project)
    await message.answer(f"Должность изменена (<b>{position}</b>).")
    await state.set_state(EditPersonal.choose)
    return await message.answer("Выберите что хотите сделать.", reply_markup=kb.edit_kb)


@router.message(EditPersonal.project, RoleFilter(['admin']), BannedFilter(False))
async def project_handler(message: types.Message, state: FSMContext):
    project = message.text.strip()
    data = await state.get_data()
    data['project'] = project
    await state.set_data(data)
    await state.set_state(AddPersonal.avatar)
    await message.answer(f"Проект изменен (<b>{project}</b>).")
    await state.set_state(EditPersonal.choose)
    return await message.answer("Выберите что хотите сделать.", reply_markup=kb.edit_kb)


@router.message(EditPersonal.avatar, F.content_type == 'photo', RoleFilter(['admin']), BannedFilter(False))
async def avatar_handler(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    path = f'data/img/personal/{photo_id}.jpg'
    await bot.download(photo_id, path)
    data = await state.get_data()
    data['avatar'] = path
    await state.set_data(data)
    await state.set_state(AddPersonal.join_time)
    await message.reply(f"Аватарка изменена.")
    await state.set_state(EditPersonal.choose)
    return await message.answer("Выберите что хотите сделать.", reply_markup=kb.edit_kb)


@router.message(EditPersonal.avatar, RoleFilter(['admin']), BannedFilter(False))
async def avatar_other_handler(message: types.Message, state: FSMContext):
    if message.text.strip() != '/del':
        return await message.answer("Необходимо отправить аватарку как фото. (отправка файлом не принимается)")
    else:
        data = await state.get_data()
        data['avatar'] = 'Null'
        await state.set_data(data)
        await state.set_state(AddPersonal.join_time)
        await message.reply(f"Аватар удален.")
        await state.set_state(EditPersonal.choose)
        return await message.answer("Выберите что хотите сделать.", reply_markup=kb.edit_kb)


@router.message(EditPersonal.join_time, RoleFilter(['admin']), BannedFilter(False))
async def date_handler(message: types.Message, state: FSMContext):
    dt = message.text.strip().split('.')
    if len(dt) != 3 or len(dt[-1]) != 4:
        return await message.answer("Неверный формат даты. Формат: дд.мм.гггг\n* Пример: <i>28.09.2023</i>")
    try:
        date = datetime.datetime(int(dt[2]), int(dt[1]), int(dt[0]))
        timestamp = date.timestamp()
    except Exception as ex:
        return await message.answer(f"Неверный формат даты ({ex})")
    data = await state.get_data()
    data["time_join"] = timestamp
    await state.set_data(data)
    await message.reply("Дата прихода изменена.")
    await state.set_state(EditPersonal.choose)
    return await message.answer("Выберите что хотите сделать.", reply_markup=kb.edit_kb)


async def confirm_edit(query: types.CallbackQuery, state: FSMContext, data: dict, personal: dict):
    txt = "<i><b>Измененные значения:</b></i>"
    params = {"full_name": "ФИО", "position": "должность", "project": "проект", "avatar": "аватарка",
              "time_join": "дата прихода"}
    for k, v in data.items():
        if k == 'personal_id':
            continue
        if k == 'time_join':
            txt += f"\n\n• Значение <b>{params[k]}</b> изменено:\n<i>" \
                   f"{datetime.datetime.fromtimestamp(personal[k]).strftime('%d.%m.%Y')}</i> -> <i>" \
                   f"{datetime.datetime.fromtimestamp(data[k]).strftime('%d.%m.%Y')}</i>"
        elif k in params:
            txt += f"\n\n• Значение <b>{params[k]}</b> изменено:\n<i>{personal[k]}</i> -> <i>{data[k]}</i>"
        await db.change_personal(data['personal_id'], k, v)
    await query.answer("Информация о сотруднике изменена.")
    await query.message.edit_text(txt, reply_markup=None)
    return await open_menu(query.message, state, edit=False)


# === Callback-хандлеры ===
# callback редактирования
@router.callback_query(EditPersonal.choose, RoleFilter(['admin']), BannedFilter(False))
async def edit_callback(query: types.CallbackQuery, state: FSMContext):
    act = query.data.strip()
    data = await state.get_data()
    personal = await db.get_personal_by_id(data['personal_id'])
    if not personal:
        await open_menu(query.message, state, edit=True)
        return await query.answer("Указанный сотрудник не найден в базе бота")
    if act == "cancel":
        await query.message.edit_reply_markup(None)
        await query.answer("Редактирование сотрудника отменено", show_alert=True)
        return await open_menu(query.message, state, edit=False)
    if act == "cancel_b":
        await state.set_state(EditPersonal.choose)
        await query.message.edit_reply_markup(None)
        return await query.message.answer("Выберите что хотите сделать.", reply_markup=kb.edit_kb)
    if act == "confirm":
        return await confirm_edit(query, state, data, personal)
    if act == "name":
        await state.set_state(EditPersonal.full_name)
        return await query.message.edit_text("Введите новое ФИО.", reply_markup=kb.cancel_b_kb)
    if act == "position":
        await state.set_state(EditPersonal.position)
        return await query.message.edit_text("Введите новую должность.", reply_markup=kb.cancel_b_kb)
    if act == "project":
        await state.set_state(EditPersonal.project)
        return await query.message.edit_text("Введите новый проект.", reply_markup=kb.cancel_b_kb)
    if act == "avatar":
        await state.set_state(EditPersonal.avatar)
        return await query.message.edit_text("Отправьте фото новой аватарки пользователя.", reply_markup=kb.cancel_b_kb)
    if act == "time_join":
        await state.set_state(EditPersonal.join_time)
        return await query.message.edit_text("Введите новую дату прихода сотрудника в формате дд.мм.гггг", reply_markup=kb.cancel_b_kb)


# callback карточки сотрудника
async def pers_callback(query: types.CallbackQuery, state: FSMContext):
    act = query.data.split(':')[1]
    if act != 'back':
        data = query.data.split(':')[2]
    else:
        return await show_list(query.message, state)
    personal = await db.get_personal_by_id(data)
    role = await get_role(query.from_user.id)
    if not personal:
        return await query.answer("Выбранный сотрудник не найден в базе бота. (возможно он был удален)", show_alert=True)
    if act == "show":
        return await show_personal(personal, query.message, role, edit=True)
    if act == "del":
        if role != "admin":
            return await show_no_permission_message(query)
        await db.del_personal(personal['personal_id'])
        await query.answer("Сотрудник удален", show_alert=True)
        await query.message.edit_reply_markup(None)
        return await open_menu(query.message, state, edit=False)
    if act == "edit":
        if role != "admin":
            return await show_no_permission_message(query)
        await state.set_state(EditPersonal.choose)
        await state.set_data({'personal_id': personal['personal_id']})
        await query.message.edit_reply_markup(None)
        return await query.message.answer("Выберите что хотите сделать.", reply_markup=kb.edit_kb)


# callback главного меню
async def main_callback(query: types.CallbackQuery, state: FSMContext):
    act = query.data.split(':')[-1]
    role = await get_role(query.from_user.id)
    if act == "back":
        return await open_menu(query.message, state, edit=True)
    if act == "menu":
        await query.message.edit_reply_markup(None)
        return await open_menu(query.message, state, edit=False)
    if act == "list":
        return await show_list(query, state, edit=True)
    if act == "search":
        return await query.message.edit_text("<b><i>Меню поиска:</i></b>", reply_markup=kb.search_kb)
    if act == "add":
        if role != "admin":
            return await show_no_permission_message(query)
        await state.set_state(AddPersonal.full_name)
        await state.set_data({})
        return await query.message.answer(f"Вы перешли в режим добавления сотрудника, для выхода введите команду /menu."
                                          f"\n\nШаг 1 из 5.\nОтправьте боту ФИО сотрудника (Отчество при наличии)")


# callback поиска
async def search_callback(query: types.CallbackQuery, state: FSMContext):
    act = query.data.split(':')[1]
    if act == "name":
        text = f"Для поиска сотрудника по ФИО просто отправьте боту сообщение с текстом поискового запроса."
        return await query.answer(text, show_alert=True)
    if act == "project_user":
        text = f"Для поиска сотрудника по ФИО внутри проекта отправьте боту сообщение с текстом поискового " \
               f"запроса, добавив перед ФИО название проекта в квадратных скобках []."
        return await query.answer(text, show_alert=True)
    if act == "project":
        return await query.message.answer("<b>Выберите проект:</b>",
                                          reply_markup=await kb.create_project_search_kb(
                                              await db.get_projects_personal()))
    if act == "position":
        text = f"Для поиска сотрудника по ФИО внутри проекта отправьте боту сообщение с текстом поискового " \
               "запроса, добавив перед ФИО должность в фигурных скобках {}."
        return await query.answer(text, show_alert=True)
    if act == "position_list":
        return await query.message.answer("<b>Выберите должность:</b>",
                                          reply_markup=await kb.create_position_search_kb(
                                              await db.get_positions_personal()))
    if act == "time":
        text = f"Для поиска сотрудника по времени прихода отправьте боту промежуток времени в формате " \
              f"\n«(дд.мм.гггг - дд.мм.гггг)».\n* После скобок можно указать ФИО." \
               f"\n* конечная/начальная дата необязательна"
        return await query.answer(text, show_alert=True)
    if act == "s_project":
        project = query.data.split(':')[-1]
        personal = await db.get_personal(active=True, project=project)
        return await show_personal_list(personal, edit=False, message=query.message, search=True)
    if act == "s_pos":
        position = query.data.split(':')[-1]
        personal = await db.get_personal(active=True, position=position)
        return await show_personal_list(personal, edit=False, message=query.message, search=True)


# основной callback хендлер
@router.callback_query(BannedFilter(False))
async def callback_handler(query: types.CallbackQuery, state: FSMContext):
    module = query.data.split(':')[0]
    if module == "main":
        return await main_callback(query, state)
    if module == "pers":
        return await pers_callback(query, state)
    if module == "cancel":
        return await open_menu(query.message, state, edit=True)
    if module == "cancel_b":
        await state.set_state(EditPersonal.choose)
        await query.message.edit_reply_markup(None)
        return await query.message.answer("Выберите что хотите сделать.", reply_markup=kb.edit_kb)
    if module == "search":
        return await search_callback(query, state)


# === Поиск ===
async def process_project_search(message: Message) -> tuple | Message:
    project = message.text.strip('[').split(']')[0].lower()
    projects = await db.get_projects_personal()
    if project not in [project_name.lower() for project_name in projects]:
        projects_txt = ''
        for proj in projects:
            projects_txt += f"\n • {proj}"
        return await message.answer(f"Проект <b>«{project}»</b> не найден.\n\nСписок проектов:{projects_txt}",
                                    reply_markup=kb.search_proj_kb)
    else:
        search = message.text.strip('[').split(']', 1)
        if len(search) < 2 or not search[-1].strip():
            return await message.answer("Запрос не должен быть пустым.")
        search_keys = message.text.strip().split(']', 1)[-1].split()
    return project, search_keys


async def process_position_search(message: Message) -> tuple | Message:
    position = message.text.strip('{').split('}')[0].lower()
    positions = await db.get_positions_personal()
    if position not in [pos.lower() for pos in positions]:
        pos_txt = ''
        for proj in positions:
            pos_txt += f"\n • {proj}"
        return await message.answer(f"Проект <b>«{position}»</b> не найден.\n\nСписок проектов:{pos_txt}",
                                    reply_markup=kb.search_pos_kb)
    else:
        search = message.text.strip('{').split('}', 1)
        if len(search) < 2 or not search[-1].strip():
            return await message.answer("Запрос не должен быть пустым.")
        search_keys = message.text.strip().split('}', 1)[-1].split()
    return position, search_keys


async def process_time_search(message: Message) -> tuple | Message:
    async def show_err_msg() -> Message:
        return await message.answer("Некорректный формат промежутка времени."
                                    "\n\nФормат: <b>«(дд.мм.гггг - дд.мм.гггг)»</b>."
                                    "\n\nПример: <i>(1.10.2022 - 28.9.2023)</i>"
                                    "\n\nили <i>(1.10.2022 - )</i> - поиск без конечной/начальной даты"
                                    "\n\nили <i>(1.10.2022 - 28.9.2023) Иванов</i> - поиск дата + ФИО")

    async def process_date(date_str: str) -> float | Message:
        if not date_str.strip():
            return await show_err_msg()
        date_str = date_str.strip().split('.')
        if len(date_str) < 3 or len(date_str[-1]) != 4:
            return await show_err_msg()
        try:
            datetime_ = datetime.datetime(int(date_str[2]), int(date_str[1]), int(date_str[0]))
            timestamp = datetime_.timestamp()
        except:
            return await show_err_msg()
        return timestamp

    time_data, search_data = message.text.strip('(').split(')')
    if len(time_data.split('-')) != 2:
        return await show_err_msg()
    start_time, end_time = time_data.split('-')
    # обработка начальной даты
    if start_time.strip():
        start_timestamp = await process_date(start_time)
    else:
        start_timestamp = 0
    # обработка конечной даты
    if end_time.strip():
        end_timestamp = await process_date(end_time)
    else:
        end_timestamp = time.time() + 24 * 60 * 60
    if not search_data.strip():
        search_keys = ['']
    else:
        search_keys = search_data.split()
    return start_timestamp, end_timestamp, search_keys


@router.message(BannedFilter(False))
async def search_handler(message: types.Message, state: FSMContext):
    # Обработка поиска по проекту
    if message.text.startswith('['):
        project, search_keys = await process_project_search(message)
    else:
        project = False
        search_keys = message.text.strip().split()
    # Обработка поиска по проекту
    if message.text.startswith('{'):
        position, search_keys = await process_position_search(message)
    else:
        position = False
        search_keys = message.text.strip().split()
    # Обработка поиска по времени
    message_text = message.text.split(']', 1)[-1]
    message_text = message.text.split('}', 1)[-1]
    if message_text.startswith('('):
        start_time, end_time, search_keys = await process_time_search(message)
    else:
        start_time = 0
        end_time = time.time() + 24 * 60 * 60
    if not message.text.strip():
        return await message.answer("Запрос не должен быть пустым.")
    finded = []
    try:
        search_keys = [' '.join(cmb) for cmb in list(permutations(search_keys + [''], 3))] + search_keys
        added = []
        for x in search_keys:
            if search_keys == ['']:
                find_results = await db.get_personal_by_time(active=True, project=project, position=position,
                                                             time_search=(start_time, end_time))
            else:
                find_results = await db.get_personal_by_name(x.strip(), active=True, project=project, position=position,
                                                             time_search=(start_time, end_time))
            for res in find_results:
                if res['personal_id'] not in added:
                    added.append(res['personal_id'])
                    finded.append(res)
    except Exception as ex:
        logger.warning(f"error while searching (uid: {message.from_user.id}, request: {message.text.strip()})", exc_info=True)
    text = f"<b><i>🔎 Результаты поиска:</i></b>"
    if not finded:
        text += f"\n\nНикого не найдено."
    return await message.reply(text, reply_markup=await kb.create_personal_list_kb(finded, search=True))
