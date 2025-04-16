from io import BytesIO
import json
import zipfile
from aiogram import Bot
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger


from bot.config import MAX_FILE_SIZE_BYTES, RU_LANG
from bot.database.sql_operations import create_new_account, delete_account, get_account, get_account_by_cookies, get_accounts_by_name, get_user, get_user_accounts, set_category_link_account, set_cookie_account, set_count_spam_account, set_geolocation_id_account, set_is_blocked, set_is_ready_account, set_name_account, set_proxy_account, set_radius_account, set_rate_limit_account, set_text_spam_account, set_time_filter_spam_account, set_user_agent_account
from bot.keyboards import cancel_account_kb, get_accounts_inline_kb, get_inline_filter_time_choises, get_inline_radius, get_inline_user_panel, send_account_ikb
from bot.parser import FaceBook
from bot.states import UserStatesGroup
from bot.utils import convert_cookie_json, convert_cookie_netscape, validate_user_subscription


async def cmd_load_accounts(callback: CallbackQuery, state: FSMContext, bot: Bot):
    is_active = await validate_user_subscription(user_id=callback.from_user.id, bot=bot)
    if not is_active:
        return
    
    await state.set_state(UserStatesGroup.load_zip_accounts)
    await callback.answer(text=RU_LANG.load_zip_account)
    
async def load_zip_accounts(message: Message, state: FSMContext):
    if not message.document or not message.document.file_name.endswith(".zip"):
        await message.answer(text=RU_LANG.no_file)
        return

    if message.document.file_size > MAX_FILE_SIZE_BYTES:
        await message.answer(text=RU_LANG.file_too_big)
        return

    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_data = await message.bot.download_file(file.file_path)

    accounts_info = {}
    with zipfile.ZipFile(BytesIO(file_data.read())) as z:
        files_names = [name for name in z.namelist()]

        for file_name in files_names:
            name = file_name.split("/")[0]
            if name not in accounts_info:
                accounts_info[name] = {}

            if "user_agent.txt" in file_name.lower():
                with z.open(file_name) as f:
                    user_agent = f.read().decode("utf-8")
                    accounts_info[name]["user_agent"] = user_agent
                    
            if "cookies_json.txt" in file_name.lower():
                with z.open(file_name) as f:
                    cookie = f.read().decode("utf-8")
                    cookie = convert_cookie_json(cookie)
                    accounts_info[name]["cookie"] = cookie

    expected_accounts = len(accounts_info)
    real_success = 0
    for name, account_info in accounts_info.items():
        if not account_info.get("cookie") or not account_info.get("user_agent"):
            logger.warning(f"Account {name} is not valid: cookie or user agent not found")
            continue

        if await get_account_by_cookies(cookie=account_info["cookie"], user_id=message.from_user.id):
            logger.warning(f"Account {name} already exists for user {message.from_user.id}")
            continue

        await create_new_account(user_id=message.from_user.id, name=name, cookie=account_info["cookie"], user_agent=account_info["user_agent"])
        logger.info(f"Account {name} created for user {message.from_user.id}")
        real_success += 1


    await message.answer(
    text=f"✅ <b>Аккаунты успешно загружены!</b>\n"
        f"Загружено: {real_success} из {expected_accounts} аккаунтов.\n\n"
        f"❗️ <b>Важно!</b> Перед началом работы необходимо <b>настроить аккаунты</b>, чтобы они были готовы к спаму.\n"
        f"Вы можете настроить каждый аккаунт отдельно или применить настройки ко всем сразу.\n"
        f"<b>Будьте внимательны:</b> при массовой настройке изменения затронут абсолютно все аккаунты!\n",
        parse_mode="HTML",
        reply_markup=get_inline_user_panel()
    )

    await state.set_state(UserStatesGroup.menu)


async def cmd_my_accounts(callback: CallbackQuery, state: FSMContext, bot: Bot):
    # await delete_user(user_id=message.from_user.id)
    is_active = await validate_user_subscription(user_id=callback.from_user.id, bot=bot)
    if not is_active:
        return
    
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    if not accounts:
        await callback.answer(text=RU_LANG.no_accounts)
        return
    
    await state.set_state(UserStatesGroup.account_menu_options)
    await bot.send_message(chat_id=callback.from_user.id, text=RU_LANG.your_accounts, reply_markup=get_accounts_inline_kb(accounts, 0))
    
async def choose_page_account(callback: CallbackQuery, state: FSMContext, bot: Bot):
    page = int(callback.data.split("_")[-1])
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    await callback.message.edit_text(text=RU_LANG.your_accounts, reply_markup=get_accounts_inline_kb(accounts, page))
    
async def choose_account(callback: CallbackQuery, state: FSMContext, bot: Bot):
    account_id = int(callback.data.split("_")[-1])
    await state.set_state(UserStatesGroup.account_menu)
    await send_account_ikb(None, account_id, bot)
    
async def cmd_create_account(callback: CallbackQuery, state: FSMContext, bot: Bot):
    is_active = await validate_user_subscription(user_id=callback.from_user.id, bot=bot)
    if not is_active:
        return
    
    await callback.answer(text=RU_LANG.create_account)
    await state.set_state(UserStatesGroup.create_account)
    
async def create_account(message: Message, state: FSMContext):
    await create_new_account(user_id=message.from_user.id, name=message.text)
    logger.info(f"Account created: {message.text} for user {message.from_user.id}")
    accounts = await get_accounts_by_name(name=message.text, user_id=message.from_user.id)
    max_id = 0
    for index, account in enumerate(accounts):
        if account['id'] > max_id:
            max_id = account['id']
            index_account = index

    account = accounts[index_account]
    message_text = (
        "✅ <b>Ваш аккаунт успешно создан!</b>\n"
        "Однако он пока <b>не готов к спаму</b>, так как не были предоставлены необходимые данные.\n\n"
        "📥 Пожалуйста, предоставьте следующие данные:\n\n"
        "1️⃣ <b>Cookie</b> — лог в виде .txt файла\n"
        "2️⃣ <b>Proxy URL</b> — строка вида(socks5):\n"
        "<code>user:password@ip:port</code>\n"
        "3️⃣ <b>User Agent</b> — строка из лога, в виде текста\n"
        "4️⃣ <b>Count Spam</b> — сколько объявлений должен проспамить аккаунт\n"
        "5️⃣ <b>Category Link</b> — ссылка на категорию товаров для спама <i>(необязательно)</i>\n"
        "   — по умолчанию: спам по всем объявлениям\n"
        "6️⃣ <b>Geolocation</b> — название города <b>на английском</b>, пример: <code>Moscow</code> <i>(необязательно)</i>\n"
        "   — по умолчанию используется начальная геолокация аккаунта\n"
        "7️⃣ <b>Radius</b> — радиус поиска в км <i>(необязательно)</i>:\n"
        "<code>1, 2, 5, 10, 20, 40, 60, 80, 100, 250, 500</code>\n"
        "   — по умолчанию используется изначальный\n"
        "8️⃣ <b>Text Spam</b> — текст, который будет отправляться в спаме\n"
        "9️⃣ <b>Time Filter Spam</b> — фильтр по дате размещения объявлений <i>(необязательно)</i>:\n"
        "<code>1, 2, 4, 8, 16, 24 ч (24 ч — лучший выбор), неделя, месяц</code>\n"
        "   — по умолчанию: любые объявления\n"
        "🔟 <b>Rate Limit</b> — задержка между сообщениями в секундах <i>(необязательно)</i>\n"
        "   — по умолчанию: 20 секунд\n\n"
        "✅ После предоставления всех данных аккаунт будет готов к спаму.\n"
        "🔍 Нажмите кнопку <b>Check Valid</b>, чтобы проверить валидность аккаунта.\n"
        "📤 После этого вы сможете запускать спам.\n\n"
        "🗑 Если хотите удалить аккаунт — нажмите <b>Delete Account</b>.\n"
    )


    await message.answer(text=message_text, parse_mode="HTML")

    await send_account_ikb(message, account['id'])
    await state.set_state(UserStatesGroup.account_menu)
    
async def set_cookie_callback(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_cookie)
    await callback.message.edit_text(text=RU_LANG.send_cookies, reply_markup=cancel_account_kb(account_id))
    
async def set_cookie(message: Message, state: FSMContext):
    info = await state.get_data()
    account_id = info.get("account_id")
    
    if not message.document or not message.document.file_name.endswith(".txt"):
        await message.answer(text=RU_LANG.no_file)
        return
    
    if message.document.file_size > MAX_FILE_SIZE_BYTES:
        await message.answer(text=RU_LANG.file_too_big)
        return
    
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    
    file_data = await message.bot.download_file(file.file_path)
    cookie = file_data.read().decode("utf-8")
    try:
        cookie = convert_cookie_json(cookie)
    except json.JSONDecodeError:
        cookie = convert_cookie_netscape(cookie)
    
    logger.info(f"Account {account_id} cookie set")
    await set_cookie_account(account_id=account_id, cookie=cookie)
    await send_account_ikb(message, account_id)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def set_user_agent_callback(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_user_agent)
    await callback.message.edit_text(text=RU_LANG.send_user_agent, reply_markup=cancel_account_kb(account_id))
    
async def set_user_agent(message: Message, state: FSMContext):
    info = await state.get_data()
    account_id = info.get("account_id")
    await set_user_agent_account(account_id=account_id, user_agent=message.text)
    logger.info(f"Account {account_id} user agent set")
    await send_account_ikb(message, account_id)
    
    await state.set_state(UserStatesGroup.account_menu)

async def set_proxy_callback(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_proxy_url)
    await callback.message.edit_text(text=RU_LANG.send_proxy_url, reply_markup=cancel_account_kb(account_id))
    
async def set_proxy(message: Message, state: FSMContext):
    info = await state.get_data()
    account_id = info.get("account_id")
    await set_proxy_account(account_id=account_id, proxy_url=message.text)
    logger.info(f"Account {account_id} proxy url set")
    await send_account_ikb(message, account_id)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def set_text_spam_callback(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_text_spam)
    await callback.message.edit_text(text=RU_LANG.send_text_spam, reply_markup=cancel_account_kb(account_id))
    
async def set_text_spam(message: Message, state: FSMContext):
    info = await state.get_data()
    account_id = info.get("account_id")
    await set_text_spam_account(account_id=account_id, text_spam=message.text)
    logger.info(f"Account {account_id} text spam set")
    await send_account_ikb(message, account_id)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def set_count_spam_callback(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_count_spam)
    await callback.message.edit_text(text=RU_LANG.send_count_spam, reply_markup=cancel_account_kb(account_id))
    
async def set_count_spam(message: Message, state: FSMContext):
    info = await state.get_data()
    account_id = info.get("account_id")
    if not account_id:
        await message.answer(text=RU_LANG.no_account)
        return
    
    try:
        count_spam = int(message.text)
    except ValueError:
        await message.answer(text=RU_LANG.bad_format)
        return
    
    await set_count_spam_account(account_id=account_id, count_spam=count_spam)
    logger.info(f"Account {account_id} count spam set")
    await send_account_ikb(message, account_id)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def set_category_link_callback(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_category_link)
    await callback.message.edit_text(text=RU_LANG.send_category_link, reply_markup=cancel_account_kb(account_id))
    
async def set_category_link(message: Message, state: FSMContext):
    info = await state.get_data()
    account_id = info.get("account_id")
    
    await set_category_link_account(account_id=account_id, category_link=message.text)
    logger.info(f"Account {account_id} category link set")
    await send_account_ikb(message, account_id)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def set_geolocation_id_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    account_id = int(callback.data.split("_")[-1])
    account = await get_account(account_id=account_id)
    if not account['is_ready']:
        await callback.message.delete()
        await callback.message.answer(text=RU_LANG.no_account_fullfilled)
    else:
        await state.set_data({"account_id": account_id})
        await state.set_state(UserStatesGroup.set_geolocation_id)
        await callback.message.edit_text(text=RU_LANG.send_geolocation, reply_markup=cancel_account_kb(account_id))
        return
    
    await send_account_ikb(None, account_id, bot)
    
async def set_geolocation_id(message: Message, state: FSMContext):
    info = await state.get_data()
    account_id = info.get("account_id")
    if not account_id:
        await message.answer(text=RU_LANG.no_account)
        return
    
    if not message.text:
        await message.answer(text=RU_LANG.no_file)
        return
    parser = FaceBook()
    account = await get_account(account_id=account_id)
    geolocation_id = await parser.change_geolocation(account=account, query=message.text)
    if not geolocation_id:
        await message.answer(text=RU_LANG.geolocation_id_not_found)
    else:
        await set_geolocation_id_account(account_id=account_id, geolocation_id=geolocation_id)
        logger.info(f"Account {account_id} geolocation id set to {geolocation_id}")
    await send_account_ikb(message, account_id)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def set_radius_callback(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    account = await get_account(account_id=account_id)
    if not account['is_ready']:
        await Message.answer(text=RU_LANG.no_account_fullfilled)
        return
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_radius)
    await callback.message.edit_text(text=RU_LANG.send_radius, reply_markup=get_inline_radius(account_id))
    
async def set_radius(callback: CallbackQuery, state: FSMContext, bot: Bot):
    radius = int(callback.data.split("_")[-1])
    info = await state.get_data()
    account_id = info.get("account_id")
    
    account = await get_account(account_id=account_id)
    parser = FaceBook()
    if not await parser.change_radius(account=account, radius=radius):
        await callback.answer(text=RU_LANG.radius_not_found)
        await set_is_blocked(account_id=account_id, is_blocked=True)
        logger.warning(f"Account {account_id} is blocked: reason: cannot change radius")
    else:
        await set_radius_account(account_id=account_id, radius=radius)

    await callback.message.delete()
    await send_account_ikb(None, account_id, bot)
    logger.info(f"Account {account_id} radius changed to {radius}")
    await state.set_state(UserStatesGroup.account_menu)
    
async def set_time_filter_callback(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_time_filter)
    await callback.message.edit_text(text=RU_LANG.send_time_filter, reply_markup=get_inline_filter_time_choises(account_id))
    
    
async def set_time_filter(callback: CallbackQuery, state: FSMContext, bot: Bot):
    info = await state.get_data()
    account_id = info.get("account_id")
    filter_time_id = int(callback.data.split("_")[-1])
    await set_time_filter_spam_account(account_id=account_id, time_filter_spam_id=filter_time_id)
    logger.info(f"Account {account_id} time filter changed to {filter_time_id}")
    await callback.message.delete()
    await send_account_ikb(None, account_id, bot)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def set_rate_limit_callback(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_rate_limit)
    await callback.message.edit_text(text=RU_LANG.send_rate_limit, reply_markup=cancel_account_kb(account_id))
    
async def set_rate_limit(message: Message, state: FSMContext):
    info = await state.get_data()
    account_id = info.get("account_id")
    try:
        rate_limit = int(message.text)
    except ValueError:
        await message.answer(text=RU_LANG.bad_format)
        return
    
    await set_rate_limit_account(account_id=account_id, rate_limit=rate_limit)
    logger.info(f"Account {account_id} rate limit changed to {rate_limit}")
    await send_account_ikb(message, account_id)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def callback_set_name(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await state.set_data({"account_id": account_id})
    await state.set_state(UserStatesGroup.set_name)
    await callback.message.edit_text(text=RU_LANG.send_name, reply_markup=cancel_account_kb(account_id))
    
async def set_name(message: Message, state: FSMContext):
    info = await state.get_data()
    account_id = info.get("account_id")
    
    if not message.text:
        await message.answer(text=RU_LANG.no_file)
        return
    
    await set_name_account(account_id=account_id, name=message.text)
    logger.info(f"Account {account_id} name changed to {message.text}")
    await send_account_ikb(message, account_id)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def callback_validate_account_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    account_id = int(callback.data.split("_")[-1])
    account = await get_account(account_id=account_id)
    if not (account['cookie'] and account['user_agent'] and account['proxy_url'] and account['text_spam'] and account['count_spam']):
        await callback.message.answer(text=RU_LANG.not_fullfilled)
    else:
        parser = FaceBook()
        await callback.message.edit_text(text=RU_LANG.checking_account)
        if await parser.login_by_cookies(account=account):
            await callback.message.delete()
            logger.info(f"Account {account_id} is valid")
            await set_is_ready_account(account_id=account_id)
        else:
            await callback.message.delete()
            await set_is_blocked(account_id=account_id, is_blocked=True)
            await callback.message.answer(text=RU_LANG.account_not_valid)
    
    await send_account_ikb(None, account_id, bot)
    
    await state.set_state(UserStatesGroup.account_menu)
    
async def callback_delete_account(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    await delete_account(account_id=account_id)
    logger.info(f"Account {account_id} deleted")
    await callback.message.answer(text=RU_LANG.account_deleted)
    
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    if not accounts:
        await callback.message.answer(text=RU_LANG.menu)
        await state.set_state(UserStatesGroup.menu)
        return
    
    await callback.message.edit_text(text=RU_LANG.your_accounts, reply_markup=get_accounts_inline_kb(accounts, 0))
    
    await state.set_state(UserStatesGroup.account_menu_options)

async def callback_cancel_account(callback: CallbackQuery, state: FSMContext):
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    if not accounts:
        await callback.message.answer(text=RU_LANG.menu)
        await state.set_state(UserStatesGroup.menu)
        return
    await callback.message.edit_text(text=RU_LANG.your_accounts, reply_markup=get_accounts_inline_kb(accounts, 0))
    await state.set_state(UserStatesGroup.account_menu_options)
    
async def callback_cancel_action_account(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.delete()
    account_id = int(callback.data.split("_")[-1])
    await send_account_ikb(None, account_id, bot)
    await state.set_state(UserStatesGroup.account_menu)
