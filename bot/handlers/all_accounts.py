import asyncio
from aiogram import Bot
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger


from bot.config import RU_LANG
from bot.database.sql_operations import delete_account, get_user_accounts, set_category_link_account, set_count_spam_account, set_geolocation_id_account, set_is_blocked, set_is_ready_account, set_name_account, set_proxy_account, set_radius_account, set_rate_limit_account, set_text_spam_account, set_time_filter_spam_account
from bot.keyboards import cancel_configure_account_kb, get_configure_inline_filter_time_choises, get_configure_inline_radius, get_inline_user_panel, send_configure_accounts_ikb
from bot.parser import FaceBook
from bot.states import UserStatesGroup
from bot.utils import validate_user_subscription


async def cmd_configure_accounts(callback: CallbackQuery, state: FSMContext, bot: Bot):
    # await delete_user(user_id=message.from_user.id)
    is_active = await validate_user_subscription(user_id=callback.from_user.id, bot=bot)
    if not is_active:
        return
    
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    if not accounts:
        await callback.answer(text=RU_LANG.no_accounts)
        return
    
    await state.set_state(UserStatesGroup.account_configure_menu)
    await send_configure_accounts_ikb(None, callback.from_user.id, bot)

async def set_configure_proxy_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatesGroup.set_configure_proxy_url)
    await callback.message.edit_text(text=RU_LANG.send_proxy_url, reply_markup=cancel_configure_account_kb())
    
async def set_configure_proxy(message: Message, state: FSMContext):
    accounts = await get_user_accounts(user_id=message.from_user.id)
    for account in accounts:
        await set_proxy_account(account_id=account["id"], proxy_url=message.text)
        logger.info(f"Account {account['id']} proxy url set")
    
    await send_configure_accounts_ikb(message, message.from_user.id)
    await state.set_state(UserStatesGroup.account_configure_menu)
    
async def set_configure_text_spam_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatesGroup.set_configure_text_spam)
    await callback.message.edit_text(text=RU_LANG.send_text_spam, reply_markup=cancel_configure_account_kb())
    
async def set_configure_text_spam(message: Message, state: FSMContext):
    accounts = await get_user_accounts(user_id=message.from_user.id)
    for account in accounts:
        await set_text_spam_account(account_id=account["id"], text_spam=message.text)
        logger.info(f"Account {account['id']} text spam set")
    
    await send_configure_accounts_ikb(message, message.from_user.id)
    await state.set_state(UserStatesGroup.account_configure_menu)
    
async def set_configure_count_spam_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatesGroup.set_configure_count_spam)
    await callback.message.edit_text(text=RU_LANG.send_count_spam, reply_markup=cancel_configure_account_kb())
    
async def set_configure_count_spam(message: Message, state: FSMContext):
    try:
        count_spam = int(message.text)
    except ValueError:
        await message.answer(text=RU_LANG.bad_format)
        return
    
    accounts = await get_user_accounts(user_id=message.from_user.id)
    for account in accounts:
        await set_count_spam_account(account_id=account["id"], count_spam=count_spam)
        logger.info(f"Account {account['id']} count spam set")
        
    await send_configure_accounts_ikb(message, message.from_user.id)
    await state.set_state(UserStatesGroup.account_configure_menu)
    
async def set_configure_category_link_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatesGroup.set_configure_category_link)
    await callback.message.edit_text(text=RU_LANG.send_category_link, reply_markup=cancel_configure_account_kb())
    
async def set_configure_category_link(message: Message, state: FSMContext):
    accounts = await get_user_accounts(user_id=message.from_user.id)
    for account in accounts:
        await set_category_link_account(account_id=account["id"], category_link=message.text)
        logger.info(f"Account {account['id']} category link set")

    await send_configure_accounts_ikb(message, message.from_user.id)
    await state.set_state(UserStatesGroup.account_configure_menu)
    
async def set_configure_geolocation_id_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    for account in accounts:
        if account['is_ready']:
            await state.set_state(UserStatesGroup.set_configure_geolocation_id)
            await callback.message.edit_text(text=RU_LANG.send_geolocation, reply_markup=cancel_configure_account_kb())
            return
        
    await callback.message.delete()
    await callback.message.answer(text=RU_LANG.no_any_account_fullfilled)
    
    await send_configure_accounts_ikb(None, callback.from_user.id, bot)
    
async def set_configure_geolocation_id(message: Message, state: FSMContext, bot: Bot):
    accounts = await get_user_accounts(user_id=message.from_user.id)
    geolocation_accounts = [account for account in accounts if account['is_ready']]
    
    await message.answer(text=f"Начат процесс установки геолокаций({len(geolocation_accounts)} запущено аккаунтов)")
    asyncio.create_task(routine_set_geolocation_id(bot=bot, accounts=geolocation_accounts, query=message.text))

    await send_configure_accounts_ikb(message, message.from_user.id)
    await state.set_state(UserStatesGroup.account_configure_menu)
    
async def routine_set_geolocation_id(bot: Bot, accounts: list[dict], query: str):
    parser = FaceBook()
    success = 0
    for account in accounts:
        geolocation_id = await parser.change_geolocation(account=account, query=query)
        if not geolocation_id:
            logger.warning(f"Account {account['id']} geolocation id not found")
        else:
            if geolocation_id == "error":
                await set_is_blocked(account_id=account["id"], is_blocked=True)
                logger.warning(f"Account {account['id']} is blocked: reason: cannot change geolocation")
                continue
            success += 1
            await set_geolocation_id_account(account_id=account["id"], geolocation_id=geolocation_id)
            logger.info(f"Account {account['id']} geolocation id set to {geolocation_id}")
            
    await bot.send_message(chat_id=accounts[0]['user_id'], text=f"Установлено {success} геолокаций из {len(accounts)}")

async def set_configure_radius_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    for account in accounts:
        if account['is_ready']:
            await state.set_state(UserStatesGroup.set_configure_radius)
            await callback.message.edit_text(text=RU_LANG.send_radius, reply_markup=get_configure_inline_radius())
            return
        
    await bot.send_message(chat_id=callback.from_user.id, text=RU_LANG.no_any_account_fullfilled)
    await callback.message.delete()
    await send_configure_accounts_ikb(None, callback.from_user.id, bot)

async def set_configure_radius(callback: CallbackQuery, state: FSMContext, bot: Bot):
    radius = int(callback.data.split("_")[-1])
    
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    radius_accounts = [account for account in accounts if account['is_ready']]
    await bot.send_message(chat_id=callback.from_user.id, text=f"Начат процесс установки радиуса({len(radius_accounts)} запущено аккаунтов)")
    asyncio.create_task(routine_set_radius(bot=bot, accounts=radius_accounts, radius=radius))

    await callback.message.delete()
    await send_configure_accounts_ikb(None, callback.from_user.id, bot)
    await state.set_state(UserStatesGroup.account_configure_menu)
    
async def routine_set_radius(bot: Bot, accounts: list[dict], radius: int):
    parser = FaceBook()
    success = 0
    for account in accounts:
        if not await parser.change_radius(account=account, radius=radius):
            await set_is_blocked(account_id=account["id"], is_blocked=True)
            logger.warning(f"Account {account['id']} is blocked: reason: cannot change radius")
        else:
            await set_radius_account(account_id=account["id"], radius=radius)
            logger.info(f"Account {account['id']} radius set to {radius}")
            success += 1
            
    await bot.send_message(chat_id=accounts[0]['user_id'], text=f"Установлено {success} радиусов из {len(accounts)}")
                
    
    
async def set_configure_time_filter_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatesGroup.set_configure_time_filter)
    await callback.message.edit_text(text=RU_LANG.send_time_filter, reply_markup=get_configure_inline_filter_time_choises())
    
    
async def set_configure_time_filter(callback: CallbackQuery, state: FSMContext, bot: Bot):
    filter_time_id = int(callback.data.split("_")[-1])
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    for account in accounts:
        await set_time_filter_spam_account(account_id=account["id"], time_filter_spam_id=filter_time_id)
        logger.info(f"Account {account['id']} time filter set to {filter_time_id}")

    await callback.message.delete()
    await send_configure_accounts_ikb(None, callback.from_user.id, bot)
    await state.set_state(UserStatesGroup.account_configure_menu)
    
async def set_configure_rate_limit_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatesGroup.set_configure_rate_limit)
    await callback.message.edit_text(text=RU_LANG.send_rate_limit, reply_markup=cancel_configure_account_kb())
    
async def set_configure_rate_limit(message: Message, state: FSMContext):
    try:
        rate_limit = int(message.text)
    except ValueError:
        await message.answer(text=RU_LANG.bad_format)
        return
    accounts = await get_user_accounts(user_id=message.from_user.id)
    for account in accounts:
        await set_rate_limit_account(account_id=account["id"], rate_limit=rate_limit)
        logger.info(f"Account {account['id']} rate limit set to {rate_limit}")

    await send_configure_accounts_ikb(message, message.from_user.id)
    await state.set_state(UserStatesGroup.account_configure_menu)
    
async def callback_validate_configure_account_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    accounts = await get_user_accounts(user_id=callback.from_user.id)

    validation_accounts = []
    for account in accounts:
        if not (account['cookie'] and account['user_agent'] and account['proxy_url'] and account['text_spam'] and account['count_spam']):
            logger.warning(f"Account {account['id']} is not fullfilled for validation")
        else:
            validation_accounts.append(account)
    
    if len(validation_accounts) == 0:
        await callback.answer(text=RU_LANG.no_any_account_fullfilled)
        return

    await bot.send_message(chat_id=callback.from_user.id, text=f"начат процесс валидации аккаунтов({len(validation_accounts)} запущено)")
    asyncio.create_task(routine_validate_accounts(bot=bot, accounts=validation_accounts))
    await send_configure_accounts_ikb(None, callback.from_user.id, bot)
    
    await state.set_state(UserStatesGroup.account_configure_menu)
    
async def routine_validate_accounts(bot: Bot, accounts: list[dict]):
    parser = FaceBook()
    success = 0
    for account in accounts:
        try:
            if not await parser.login_by_cookies(account=account):
                logger.warning(f"Account {account['id']} didn't login by cookies")
            else:
                await set_is_ready_account(account_id=account["id"])
                logger.info(f"Account {account['id']} is valid")
                success += 1
        except Exception as e:
            logger.error(f"Account {account['id']} error: {e}")
            
    await bot.send_message(chat_id=accounts[0]['user_id'], text=f"Валидация завершена, {success} аккаунтов валидны из {len(accounts)}, на оставшихся аккаунтах нужно проверить валидность куки, юзер-агентов, прокси")
    
async def callback_configure_delete_configure(callback: CallbackQuery, state: FSMContext):
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    for account in accounts:
        await delete_account(account_id=account['id'])
        logger.info(f"Account {account['id']} deleted")
    await callback.message.answer(text=RU_LANG.account_deleted)
    
    accounts = await get_user_accounts(user_id=callback.from_user.id)
    if not accounts:
        await callback.message.answer(text=RU_LANG.menu)
        await state.set_state(UserStatesGroup.menu)
        return
    
    await callback.message.edit_text(text=RU_LANG.deleted_accounts, reply_markup=get_inline_user_panel())
    await state.set_state(UserStatesGroup.menu)
    
async def callback_cancel_action_configure(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.delete()
    await send_configure_accounts_ikb(None, callback.from_user.id, bot)
    await state.set_state(UserStatesGroup.account_configure_menu)
