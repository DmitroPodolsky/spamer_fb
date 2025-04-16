from aiogram.fsm.state import StatesGroup, State

class UserStatesGroup(StatesGroup):
    menu = State()

    buy_subscription = State()
    choose_currency = State()

    create_account = State()
    account_menu = State()
    account_menu_options = State()
    load_zip_accounts = State()

    set_cookie = State()
    set_user_agent = State()
    set_proxy_url = State()
    set_text_spam = State()
    set_count_spam = State()
    set_category_link = State()
    set_geolocation_id = State()
    set_radius = State()
    set_time_filter = State()
    set_rate_limit = State()
    set_name = State()
    
    set_configure_proxy_url = State()
    set_configure_text_spam = State()
    set_configure_count_spam = State()
    set_configure_category_link = State()
    set_configure_geolocation_id = State()
    set_configure_radius = State()
    set_configure_time_filter = State()
    set_configure_rate_limit = State()
    account_configure_menu = State()

