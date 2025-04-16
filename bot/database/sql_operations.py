from datetime import datetime
from bot.database.database_operations import execute_query, fetch_query

def convert_sqlite_row_to_dict(rows):
    """
    Convert a list of sqlite3.Row objects to a list of dictionaries.
    Each dictionary represents a row, with column names as keys.
    """
    return [dict(row) for row in rows]

async def create_new_user(user_id: int):
    query = """
        INSERT INTO user (id, time_created)
        VALUES (?, datetime('now'))
    """
    await execute_query(query, (user_id,))
    
async def get_user(user_id: int):
    query = """
        SELECT *
        FROM user
        WHERE id = ?
    """
    result = convert_sqlite_row_to_dict(await fetch_query(query, (user_id,)))
    if result:
        return result[0]

async def create_new_account(
    user_id: int, name: str, cookie: str = "", rate_limit: int = 20,
    proxy_url: str = "", user_agent: str = "", text_spam: str = "",
    count_spam: int = 0, category_link: str = "", geolocation_id: int = 0,
    radius: int = 500):
    query = """
        INSERT INTO account (user_id, name, cookie, rate_limit, proxy_url, user_agent, text_spam, count_spam, category_link, geolocation_id, radius)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    await execute_query(query, (user_id, name, cookie, rate_limit, proxy_url, user_agent, text_spam, count_spam, category_link, geolocation_id, radius))
    
async def get_account(account_id: int):
    query = """
        SELECT *
        FROM account
        WHERE id = ?
    """
    result = convert_sqlite_row_to_dict(await fetch_query(query, (account_id,)))
    if result:
        return result[0]

async def get_accounts_by_name(name: str, user_id: int):
    query = """
        SELECT *
        FROM account
        WHERE name = ? AND user_id = ?
    """
    return convert_sqlite_row_to_dict(await fetch_query(query, (name, user_id)))

async def get_account_by_cookies(cookie: str, user_id: int):
    query = """
        SELECT *
        FROM account
        WHERE cookie = ? AND user_id = ?
    """
    result = convert_sqlite_row_to_dict(await fetch_query(query, (cookie, user_id)))
    if result:
        return result[0]
    
async def set_rate_limit_account(account_id: int, rate_limit: int):
    query = """
        UPDATE account
        SET rate_limit = ?
        WHERE id = ?
    """
    await execute_query(query, (rate_limit, account_id))
    
async def set_proxy_account(account_id: int, proxy_url: str):
    query = """
        UPDATE account
        SET proxy_url = ?
        WHERE id = ?
    """
    await execute_query(query, (proxy_url, account_id))
    
async def set_user_agent_account(account_id: int, user_agent: str):
    query = """
        UPDATE account
        SET user_agent = ?
        WHERE id = ?
    """
    await execute_query(query, (user_agent, account_id))
    
async def set_text_spam_account(account_id: int, text_spam: str):
    query = """
        UPDATE account
        SET text_spam = ?
        WHERE id = ?
    """
    await execute_query(query, (text_spam, account_id))
    
async def set_count_spam_account(account_id: int, count_spam: int):
    query = """
        UPDATE account
        SET count_spam = ?
        WHERE id = ?
    """
    await execute_query(query, (count_spam, account_id))
    
async def set_category_link_account(account_id: int, category_link: str):
    query = """
        UPDATE account
        SET category_link = ?
        WHERE id = ?
    """
    await execute_query(query, (category_link, account_id))
    
async def set_geolocation_id_account(account_id: int, geolocation_id: int):
    query = """
        UPDATE account
        SET geolocation_id = ?
        WHERE id = ?
    """
    await execute_query(query, (geolocation_id, account_id))
    
async def set_radius_account(account_id: int, radius: int):
    query = """
        UPDATE account
        SET radius = ?
        WHERE id = ?
    """
    await execute_query(query, (radius, account_id))
    
async def set_category_link_account(account_id: int, category_link: str):
    query = """
        UPDATE account
        SET category_link = ?
        WHERE id = ?
    """
    await execute_query(query, (category_link, account_id))
    
async def set_name_account(account_id: int, name: str):
    query = """
        UPDATE account
        SET name = ?
        WHERE id = ?
    """
    await execute_query(query, (name, account_id))
    
async def set_cookie_account(account_id: int, cookie: str):
    query = """
        UPDATE account
        SET cookie = ?
        WHERE id = ?
    """
    await execute_query(query, (cookie, account_id))
    
async def set_time_filter_spam_account(account_id: int, time_filter_spam_id: int):
    query = """
        UPDATE account
        SET time_filter_spam_id = ?
        WHERE id = ?
    """
    await execute_query(query, (time_filter_spam_id, account_id))
    
async def delete_account(account_id: int):
    query = """
        DELETE FROM account
        WHERE id = ?
    """
    await execute_query(query, (account_id,))
    
async def set_is_blocked(account_id: int, is_blocked: bool):
    query = """
        UPDATE account
        SET is_blocked = ?, is_ready = FALSE
        WHERE id = ?
    """
    await execute_query(query, (is_blocked, account_id))
    
async def set_is_ready_account(account_id: int):
    query = """
        UPDATE account
        SET is_ready = TRUE, is_blocked = FALSE
        WHERE id = ?
    """
    await execute_query(query, (account_id,))
    
async def get_user_accounts(user_id: int):
    query = """
        SELECT *
        FROM account
        WHERE user_id = ?
    """
    return convert_sqlite_row_to_dict(await fetch_query(query, (user_id, )))

async def get_user_accounts_ready(user_id: int):
    query = """
        SELECT *
        FROM account
        WHERE user_id = ? AND is_ready = TRUE
    """
    return convert_sqlite_row_to_dict(await fetch_query(query, (user_id, )))

async def create_product(product_id: int):
    query = """
        INSERT INTO product (id)
        VALUES (?)
    """
    await execute_query(query, (product_id,))
    
async def set_status_product(product_id: int, status: str):
    query = """
        UPDATE product
        SET status = ?
        WHERE id = ?
    """
    await execute_query(query, (status, product_id))
    
async def get_products():
    query = """
        SELECT *
        FROM product
    """
    return convert_sqlite_row_to_dict(await fetch_query(query))

async def set_is_spamed(product_id: int, is_spamed: bool, status: str = "success"):
    query = """
        UPDATE product
        SET is_spamed = ?, status = ?
        WHERE id = ?
    """
    await execute_query(query, (is_spamed, status, product_id))
    
    
async def create_payment(user_id: int, deadline: str, invoice_id: int, is_active: bool = False):
    query = """
        INSERT INTO payment (user_id, time_created, deadline, invoice_id, is_active)
        VALUES (?, ?, ?, ?, ?)
    """
    await execute_query(query, (user_id, datetime.now(), deadline, invoice_id, is_active))
    
async def get_user_payments(user_id: int):
    query = """
        SELECT *
        FROM payment
        WHERE user_id = ?
    """
    return convert_sqlite_row_to_dict(await fetch_query(query, (user_id,)))

async def get_payments(is_active: bool = False, is_paid: bool = False):
    query = """
        SELECT *
        FROM payment
        WHERE is_active = ? AND is_paid = ? AND is_expired = FALSE
    """
    return convert_sqlite_row_to_dict(await fetch_query(query, (is_active, is_paid)))

async def set_active_payment(payment_id: int, is_active: bool):
    query = """
        UPDATE payment
        SET is_active = ?
        WHERE id = ?
    """
    await execute_query(query, (is_active, payment_id))
    
async def set_expired_payment(payment_id: int, is_expired: bool):
    query = """
        UPDATE payment
        SET is_expired = ?
        WHERE id = ?
    """
    await execute_query(query, (is_expired, payment_id))
    
async def set_paid_payment(payment_id: int, is_paid: bool):
    query = """
        UPDATE payment
        SET is_paid = ?, is_active = TRUE
        WHERE invoice_id = ?
    """
    await execute_query(query, (is_paid, payment_id))
