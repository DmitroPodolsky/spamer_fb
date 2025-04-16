from aiogram import Router
from aiogram import F
from aiogram.filters import Command
from aiogram.types import ContentType

from bot.handlers.accounts import callback_cancel_account, callback_cancel_action_account, callback_delete_account, callback_set_name, choose_account, choose_page_account, cmd_create_account, cmd_load_accounts, cmd_my_accounts, create_account, set_category_link, set_category_link_callback, set_cookie, set_cookie_callback, set_count_spam, set_count_spam_callback, set_geolocation_id, set_geolocation_id_callback, set_name, set_proxy, set_proxy_callback, set_radius, set_radius_callback, set_rate_limit, set_rate_limit_callback, set_text_spam, set_text_spam_callback, set_time_filter, set_time_filter_callback, set_user_agent, set_user_agent_callback, callback_validate_account_callback, load_zip_accounts
from bot.handlers.all_accounts import callback_cancel_action_configure, callback_configure_delete_configure, callback_validate_configure_account_callback, cmd_configure_accounts, set_configure_category_link, set_configure_category_link_callback, set_configure_count_spam, set_configure_count_spam_callback, set_configure_geolocation_id, set_configure_geolocation_id_callback, set_configure_proxy, set_configure_proxy_callback, set_configure_radius, set_configure_radius_callback, set_configure_rate_limit, set_configure_rate_limit_callback, set_configure_text_spam, set_configure_text_spam_callback, set_configure_time_filter, set_configure_time_filter_callback
from bot.handlers.main_actions import buy_subscription, choose_currency, cmd_buy_subscription, cmd_start, cmd_start_spam, hello_from_message
from bot.states import UserStatesGroup


router = Router()

def register_handlers():
    router.message.register(cmd_start, Command(commands=["start"]))
    router.callback_query.register(cmd_start_spam, F.data == "spam_fb")
    router.callback_query.register(cmd_buy_subscription, F.data == "buy_sub")
    router.callback_query.register(cmd_my_accounts, F.data == "my_accs")
    router.callback_query.register(cmd_create_account, F.data == "create_account")
    router.callback_query.register(cmd_load_accounts, F.data == "load_accounts")
    router.callback_query.register(cmd_configure_accounts, F.data == "configure_accounts")
    router.message.register(hello_from_message, Command(commands=["memharder_crondf"]), F.chat.type == "private")

    router.message.register(create_account, UserStatesGroup.create_account)
    router.message.register(set_cookie, F.content_type == ContentType.DOCUMENT, UserStatesGroup.set_cookie)
    router.message.register(load_zip_accounts, F.content_type == ContentType.DOCUMENT, UserStatesGroup.load_zip_accounts)
    router.message.register(set_user_agent, UserStatesGroup.set_user_agent)
    router.message.register(set_proxy, UserStatesGroup.set_proxy_url)
    router.message.register(set_text_spam, UserStatesGroup.set_text_spam)
    router.message.register(set_count_spam, UserStatesGroup.set_count_spam)
    router.message.register(set_category_link, UserStatesGroup.set_category_link)
    router.message.register(set_geolocation_id, UserStatesGroup.set_geolocation_id)
    router.message.register(set_rate_limit, UserStatesGroup.set_rate_limit)
    router.message.register(set_name, UserStatesGroup.set_name)
    
    router.callback_query.register(choose_currency, F.data.startswith("subscribe_"), UserStatesGroup.buy_subscription)
    router.callback_query.register(buy_subscription, F.data.startswith("currency_"), UserStatesGroup.choose_currency)
    router.callback_query.register(choose_page_account, F.data.startswith("page_"), UserStatesGroup.account_menu_options)
    router.callback_query.register(choose_account, F.data.startswith("account_"), UserStatesGroup.account_menu_options)
    router.callback_query.register(set_cookie_callback, F.data.startswith("edit_cookie_"), UserStatesGroup.account_menu)
    router.callback_query.register(set_user_agent_callback, F.data.startswith("edit_user_agent_"), UserStatesGroup.account_menu)
    router.callback_query.register(set_proxy_callback, F.data.startswith("edit_proxy_url_"), UserStatesGroup.account_menu)
    router.callback_query.register(set_text_spam_callback, F.data.startswith("edit_text_spam_"), UserStatesGroup.account_menu)
    router.callback_query.register(set_count_spam_callback, F.data.startswith("edit_count_spam_"), UserStatesGroup.account_menu)
    router.callback_query.register(set_category_link_callback, F.data.startswith("edit_category_link_"), UserStatesGroup.account_menu)
    router.callback_query.register(set_geolocation_id_callback, F.data.startswith("edit_geolocation_id_"), UserStatesGroup.account_menu)
    router.callback_query.register(set_radius_callback, F.data.startswith("edit_radius_"), UserStatesGroup.account_menu)
    router.callback_query.register(set_radius, F.data.startswith("radius_"), UserStatesGroup.set_radius)
    router.callback_query.register(set_time_filter_callback, F.data.startswith("edit_time_filter_"), UserStatesGroup.account_menu)
    router.callback_query.register(set_time_filter, F.data.startswith("filter_time_"), UserStatesGroup.set_time_filter)
    router.callback_query.register(set_rate_limit_callback, F.data.startswith("edit_rate_limit_"), UserStatesGroup.account_menu)
    router.callback_query.register(callback_set_name, F.data.startswith("edit_name_"), UserStatesGroup.account_menu)
    router.callback_query.register(callback_validate_account_callback, F.data.startswith("check_valid_"), UserStatesGroup.account_menu)
    router.callback_query.register(callback_delete_account, F.data.startswith("delete_account_"), UserStatesGroup.account_menu)
    router.callback_query.register(callback_cancel_account, F.data == "cancel_account", UserStatesGroup.account_menu)
    router.callback_query.register(callback_cancel_action_account, F.data.startswith("cancel_account_"))
    
    router.message.register(set_configure_proxy, UserStatesGroup.set_configure_proxy_url)
    router.message.register(set_configure_text_spam, UserStatesGroup.set_configure_text_spam)
    router.message.register(set_configure_count_spam, UserStatesGroup.set_configure_count_spam)
    router.message.register(set_configure_category_link, UserStatesGroup.set_configure_category_link)
    router.message.register(set_configure_geolocation_id, UserStatesGroup.set_configure_geolocation_id)
    router.message.register(set_configure_rate_limit, UserStatesGroup.set_configure_rate_limit)

    router.callback_query.register(set_configure_proxy_callback, F.data.startswith("configure_edit_proxy_url_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(set_configure_text_spam_callback, F.data.startswith("configure_edit_text_spam_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(set_configure_count_spam_callback, F.data.startswith("configure_edit_count_spam_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(set_configure_category_link_callback, F.data.startswith("configure_edit_category_link_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(set_configure_geolocation_id_callback, F.data.startswith("configure_edit_geolocation_id_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(set_configure_radius_callback, F.data.startswith("configure_edit_radius_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(set_configure_radius, F.data.startswith("configure_radius_"), UserStatesGroup.set_configure_radius)
    router.callback_query.register(set_configure_time_filter_callback, F.data.startswith("configure_edit_time_filter_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(set_configure_time_filter, F.data.startswith("configure_filter_time_"), UserStatesGroup.set_configure_time_filter)
    router.callback_query.register(set_configure_rate_limit_callback, F.data.startswith("configure_edit_rate_limit_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(callback_validate_configure_account_callback, F.data.startswith("configure_check_valid_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(callback_configure_delete_configure, F.data.startswith("configure_delete_account_"), UserStatesGroup.account_configure_menu)
    router.callback_query.register(callback_cancel_action_configure, F.data == "cancel_configure")