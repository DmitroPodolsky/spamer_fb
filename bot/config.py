import json
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from pydantic import BaseModel
from crypto_pay_api_sdk import cryptopay

from pathlib import Path

from bot.parser import FaceBook
# /home/dmytro/PythonProjects/testcrm/crmforjopa/db.sqlite3 


project_dir = Path(__file__).parent.parent
data_dir = project_dir / "locales"
photo_dir = project_dir.parent / "testcrm" / "crmforjopa"


class Settings(BaseSettings):
    """
    Settings class for loading environment variables and configurations.

    Attributes:
        model_config: Configuration for loading environment variables.
        BOT_TOKEN: Bot token for authentication.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    BOT_TOKEN: str
    CRYPTO_TOKEN: str
    TIME_SLEEP: int = 5
    SQLITE_DATABASE_PATH: Path = photo_dir/"db.sqlite3"
    MAX_FILE_SIZE_MB: int = 10
    MAX_USERS_PARSE: int = 100
    
    RU_LANG_JSON_PATH: Path = data_dir/"ru.json"
    

class BaseLocale(BaseModel):
    """
    BaseLocale class for storing localized strings used in the bot.
    """
    choose_curency: str
    choose_subscription_type: str
    welcome_message: str
    menu: str
    no_accounts: str
    your_accounts: str
    create_account: str
    enter_account_name: str
    send_cookies: str
    send_user_agent: str
    file_too_big: str
    no_file: str
    send_proxy_url: str
    send_text_spam: str
    send_count_spam: str
    send_name: str
    bad_format: str
    send_category_link: str
    send_geolocation: str
    no_account_fullfilled: str
    radius_not_found: str
    send_time_filter: str
    send_rate_limit: str
    not_fullfilled: str
    account_not_valid: str
    account_deleted: str
    no_subscription: str
    send_radius: str
    subscription_paid: str
    load_zip_account: str
    checking_account: str
    no_any_account_fullfilled: str
    next_page: str
    previous_page: str
    
settings = Settings() 


def load_bot_strings(json_path: Path) -> BaseLocale:
    """
    Load bot strings from a JSON file.

    Parameters:
        json_path (Path): Path to the JSON file containing the bot strings.

    Returns:
        BaseLocale: An instance of BaseLocale populated with the data from the JSON file.
    """
    with open(json_path, encoding="utf-8") as file:
        json_data: dict = json.load(file)
        return BaseLocale.model_validate(json_data)


RU_LANG = load_bot_strings(settings.RU_LANG_JSON_PATH)
MAX_FILE_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024
HORVAT_PARSER = FaceBook()
MEDIA = {}
FILTER_TIME_IDS = {
    0: 'любое время',
    1: '1 час',
    2: '2 часа',
    3: '4 часов',
    4: '8 часов',
    5: '12 часов',
    6: '24 часа',
    7: 'неделя',
    8: 'месяц',
}
CRYPTO = cryptopay.Crypto(settings.CRYPTO_TOKEN, testnet = False) 