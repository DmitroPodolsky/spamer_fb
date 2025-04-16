from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message

from bot.config import FILTER_TIME_IDS, RU_LANG
from bot.database.sql_operations import get_account
from bot.utils import format_bool, format_value


def get_accounts_inline_kb(accounts: list, page: int) -> InlineKeyboardMarkup:
    start_index = page * 4
    end_index = start_index + 4
    current_accounts = accounts[start_index:end_index]

    keyboard = InlineKeyboardBuilder()

    for account in current_accounts:
        keyboard.button(text=f"{account['name']} - {account['id']}", callback_data=f"account_{account['id']}")


    navigation_buttons = InlineKeyboardBuilder()
    if start_index > 0:
        navigation_buttons.button(text=RU_LANG.previous_page, callback_data=f"page_{page-1}")
    if end_index < len(accounts):
        navigation_buttons.button(text=RU_LANG.next_page, callback_data=f"page_{page+1}")

    keyboard.adjust(1)
    keyboard.attach(navigation_buttons)
    
    return keyboard.as_markup()

async def send_account_ikb(message: Message, account_id: int, bot=None):
    account = await get_account(account_id=account_id)
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="🍪 Cookie", callback_data=f"edit_cookie_{account['id']}")
    keyboard.button(text="⏱ Rate Limit", callback_data=f"edit_rate_limit_{account['id']}")
    
    keyboard.button(text="🌐 Proxy URL", callback_data=f"edit_proxy_url_{account['id']}")
    keyboard.button(text="🧭 User Agent", callback_data=f"edit_user_agent_{account['id']}")

    keyboard.button(text="🔢 Count Spam", callback_data=f"edit_count_spam_{account['id']}")
    keyboard.button(text="📎 Category Link", callback_data=f"edit_category_link_{account['id']}")

    keyboard.button(text="🏷 Name", callback_data=f"edit_name_{account['id']}")
    keyboard.button(text="🗺 Geo ID", callback_data=f"edit_geolocation_id_{account['id']}")

    keyboard.button(text="💬 Text Spam", callback_data=f"edit_text_spam_{account['id']}")
    keyboard.button(text="🔄 Radius", callback_data=f"edit_radius_{account['id']}")

    keyboard.button(text="🕒 Time Filter", callback_data=f"edit_time_filter_{account['id']}")

    keyboard.button(text="✅ Check Valid", callback_data=f"check_valid_{account['id']}")
    keyboard.button(text="🗑 Delete", callback_data=f"delete_account_{account['id']}")

    keyboard.button(text="🔙 Назад", callback_data="cancel_account")

    keyboard.adjust(2, 2, 2, 2, 2, 2, 1)

    text = (
        f"👤 <b>Аккаунт №{format_value(account.get('id'))}</b>\n\n"
        f"🍪 <b>Cookie:</b> <code>{format_value(account.get('cookie'))}</code>\n"
        f"⏱ <b>Задержка между отправкой в секундах:</b> {format_value(account.get('rate_limit'))}\n"
        f"🌐 <b>Прокси:</b> {format_value(account.get('proxy_url'))}\n"
        f"🧭 <b>User-Agent:</b> <code>{format_value(account.get('user_agent'))}</code>\n"
        f"💬 <b>Текст для спама:</b> {format_value(account.get('text_spam'))}\n"
        f"🔢 <b>Количество сообщений:</b> {format_value(account.get('count_spam'))}\n"
        f"📎 <b>Категория:</b> {format_value(account.get('category_link'))}\n"
        f"🏷 <b>Имя аккаунта:</b> {format_value(account.get('name'))}\n"
        f"🗺 <b>Гео-ID(Название города):</b> {format_value(account.get('geolocation_id'))}\n"
        f"📏 <b>Радиус (м):</b> {format_value(account.get('radius'))}\n"
        f"🕒 <b>ID фильтра спама:</b> {FILTER_TIME_IDS[account.get('time_filter_spam_id')]}\n"
        f"⛔️ <b>Заблокирован:</b> {format_bool(account.get('is_blocked'), '🚫 Да', '✅ Нет')}\n"
        f"📶 <b>Готов к работе:</b> {format_bool(account.get('is_ready'))}"
    )
    
    if not bot:
        await message.answer(text=text, reply_markup=keyboard.as_markup(), parse_mode="HTML")
        return

    await bot.send_message(
        chat_id=account['user_id'],
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML",
    )
    
def get_inline_filter_time_choises(account_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for filter_time_id, filter_time_name in FILTER_TIME_IDS.items():
        keyboard.button(text=filter_time_name, callback_data=f"filter_time_{filter_time_id}")
    keyboard.adjust(2)
    keyboard.button(text="Отменить действие", callback_data=f"cancel_account_{account_id}")
    return keyboard.as_markup()

def get_configure_inline_filter_time_choises() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for filter_time_id, filter_time_name in FILTER_TIME_IDS.items():
        keyboard.button(text=filter_time_name, callback_data=f"configure_filter_time_{filter_time_id}")
    keyboard.adjust(2)
    keyboard.button(text="Отменить действие", callback_data="cancel_configure")
    return keyboard.as_markup()

def get_inline_subscription_deadline() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="🗓 1 день — 9$", callback_data="subscribe_9")
    keyboard.button(text="📅 1 неделя — 15$", callback_data="subscribe_15")
    keyboard.button(text="🗓 1 месяц — 30$", callback_data="subscribe_30")

    keyboard.adjust(1)  # Каждая кнопка в отдельной строке

    return keyboard.as_markup()

def get_inline_currency() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    # Верхние ряды по 3 кнопки
    keyboard.button(text="USDT", callback_data="currency_usdt")
    keyboard.button(text="BUSD", callback_data="currency_busd")
    keyboard.button(text="USDC", callback_data="currency_usdc")

    keyboard.button(text="BTC", callback_data="currency_btc")
    keyboard.button(text="ETH", callback_data="currency_eth")
    keyboard.button(text="TON", callback_data="currency_ton")

    # Отдельно BNB и отмена
    keyboard.button(text="BNB", callback_data="currency_bnb")
    keyboard.button(text="Отменить действие", callback_data="cancel_payment")

    # Раскладка кнопок по строкам: 3-3-1-1
    keyboard.adjust(3, 3, 1, 1)

    return keyboard.as_markup()

def get_inline_radius(account_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="1", callback_data="radius_1")
    keyboard.button(text="2", callback_data="radius_2")
    keyboard.button(text="5", callback_data="radius_5")
    keyboard.button(text="10", callback_data="radius_10")
    keyboard.button(text="20", callback_data="radius_20")
    keyboard.button(text="40", callback_data="radius_40")
    keyboard.button(text="60", callback_data="radius_60")
    keyboard.button(text="80", callback_data="radius_80")
    keyboard.button(text="100", callback_data="radius_100")
    keyboard.button(text="250", callback_data="radius_250")
    keyboard.button(text="500", callback_data="radius_500")

    keyboard.button(text="🚫 Отменить действие", callback_data=f"cancel_account_{account_id}")

    keyboard.adjust(3, 3, 3, 2, 1)

    return keyboard.as_markup()

def get_configure_inline_radius() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="1", callback_data="configure_radius_1")
    keyboard.button(text="2", callback_data="configure_radius_2")
    keyboard.button(text="5", callback_data="configure_radius_5")
    keyboard.button(text="10", callback_data="configure_radius_10")
    keyboard.button(text="20", callback_data="configure_radius_20")
    keyboard.button(text="40", callback_data="configure_radius_40")
    keyboard.button(text="60", callback_data="configure_radius_60")
    keyboard.button(text="80", callback_data="configure_radius_80")
    keyboard.button(text="100", callback_data="configure_radius_100")
    keyboard.button(text="250", callback_data="configure_radius_250")
    keyboard.button(text="500", callback_data="configure_radius_500")

    keyboard.button(text="🚫 Отменить действие", callback_data="cancel_configure")

    keyboard.adjust(3, 3, 3, 2, 1)

    return keyboard.as_markup()

def cancel_account_kb(account_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Отменить действие", callback_data=f"cancel_account_{account_id}")

    return keyboard.as_markup()

def cancel_configure_account_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Отменить действие", callback_data=f"cancel_configure")

    return keyboard.as_markup()

def get_inline_user_panel() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    

    keyboard.button(text="🗂 Мои аккаунты", callback_data="my_accs")
    keyboard.button(text="💳 Купить подписку", callback_data="buy_sub")
    keyboard.button(text="❓ Создать аккаунт", callback_data="create_account")
    keyboard.button(text="⚙️ Спам Фейсбука", callback_data="spam_fb")
    keyboard.button(text="📊 Загрузить аккаунты", callback_data="load_accounts")
    keyboard.button(text="⚙️ Массовая Настройка аккаунтов", callback_data="configure_accounts")

    keyboard.adjust(2, 2, 2)

    return keyboard.as_markup()


async def send_configure_accounts_ikb(message: Message, user_id: int, bot=None):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="⏱ Rate Limit", callback_data=f"configure_edit_rate_limit_{user_id}")
    keyboard.button(text="🌐 Proxy URL", callback_data=f"configure_edit_proxy_url_{user_id}")

    keyboard.button(text="🔢 Count Spam", callback_data=f"configure_edit_count_spam_{user_id}")
    keyboard.button(text="📎 Category Link", callback_data=f"configure_edit_category_link_{user_id}")

    keyboard.button(text="🗺 Geo ID", callback_data=f"configure_edit_geolocation_id_{user_id}")
    keyboard.button(text="💬 Text Spam", callback_data=f"configure_edit_text_spam_{user_id}")
    
    keyboard.button(text="🔄 Radius", callback_data=f"configure_edit_radius_{user_id}")
    keyboard.button(text="🕒 Time Filter", callback_data=f"configure_edit_time_filter_{user_id}")

    keyboard.button(text="✅ Check Valid", callback_data=f"configure_check_valid_{user_id}")
    keyboard.button(text="🗑 Delete", callback_data=f"configure_delete_account_{user_id}")

    keyboard.adjust(2, 2, 2, 2, 1)

    text = "Настройки аккаунтов"
    
    if not bot:
        await message.answer(text=text, reply_markup=keyboard.as_markup(), parse_mode="HTML")
        return

    await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML",
    )