import asyncio
import json
import os
import random
import re
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from aiogram import Bot

from bot.database.sql_operations import create_product, get_account, get_products, set_is_blocked



TWO_CAPTCHA_API_KEY = os.environ.get("TWO_CAPTCHA_API_KEY")

HEADERS = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'en-US,en;q=0.9',
    'Cache-Control':'max-age=0',
    'Pragma':'akamai-x-cache-on, akamai-x-cache-remote-on, akamai-x-check-cacheable, akamai-x-get-cache-key, akamai-x-get-extracted-values, akamai-x-get-ssl-client-session-id, akamai-x-get-true-cache-key, akamai-x-serial-no, akamai-x-get-request-id,akamai-x-get-nonces,akamai-x-get-client-ip,akamai-x-feo-trace',
    'Sec-Ch-Prefers-Color-Scheme':'light',
    'Sec-Ch-Ua':'',
    'Sec-Ch-Ua-Full-Version-List':'',
    'Sec-Ch-Ua-Mobile':'?0',
    'Sec-Ch-Ua-Platform':'',
    'Sec-Ch-Ua-Platform-Version':'',
    'Sec-Fetch-Dest':'document',
    'Sec-Fetch-Mode':'navigate',
    'Sec-Fetch-Site':'same-origin',
    'Sec-Fetch-User':'?1',
    'Upgrade-Insecure-Requests':'1',
    # 'User-Agent':i,
    'Viewport-Width':'924'
}

GLOBAL_ITEMS_IDS_ACCOUNTS = {}

def get_data(req):
    try:
        av = re.search(r'"actorID":"(.*?)"',str(req)).group(1)
        __user = av
        __a = str(random.randrange(1,6))
        __hs = re.search(r'"haste_session":"(.*?)"',str(req)).group(1)
        __ccg = re.search(r'"connectionClass":"(.*?)"',str(req)).group(1)
        __rev = re.search(r'"__spin_r":(.*?),',str(req)).group(1)
        __spin_r = __rev
        __spin_b = re.search(r'"__spin_b":"(.*?)"',str(req)).group(1)
        __spin_t = re.search(r'"__spin_t":(.*?),',str(req)).group(1)
        __hsi = re.search(r'"hsi":"(.*?)"',str(req)).group(1)
        fb_dtsg = re.search(r'"DTSGInitialData",\[\],{"token":"(.*?)"}',str(req)).group(1)
        jazoest = re.search(r'jazoest=(.*?)"',str(req)).group(1)
        lsd = re.search(r'"LSD",\[\],{"token":"(.*?)"}',str(req)).group(1)
        Data = {'av':av,'__user':__user,'__a':__a,'__hs':__hs,'dpr':'1.5','__ccg':__ccg,'__rev':__rev,'__spin_r':__spin_r,'__spin_b':__spin_b,'__spin_t':__spin_t,'__hsi':__hsi,'__comet_req':'15','fb_dtsg':fb_dtsg,'jazoest':jazoest,'lsd':lsd}
        return(Data)
    except Exception as e: return({})
    
def parse_adv_html(html: str, account_id: int):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        items = soup.find('div', {'class':'x8gbvx8 x78zum5 x1q0g3np x1a02dak x1nhvcw1 x1rdy4ex xcud41i x4vbgl9 x139jcc6'}).find_all('div')
    except AttributeError:
        logger.warning(f"❌ No items found in the HTML for account {account_id}")
        return
    item_ids = []
    for item in items:
        url = item.find('a', {'role': 'link'})
        if not url:
            continue
        url = url['href']
        item_id = re.search(r'/marketplace/item/(\d+)/', url)
        if item_id:
            item_id = item_id.group(1)
            item_ids.append(item_id)

    GLOBAL_ITEMS_IDS_ACCOUNTS[account_id] = list(set(item_ids))

def get_random_user_agent():
    devices = [
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "Macintosh; Intel Mac OS X 11_0",
        "Macintosh; Intel Mac OS X 12_0",
        "X11; Linux x86_64",
    ]

    chrome_version = random.randint(125, 130)
    build_number = random.randint(0, 99999)

    device = random.choice(devices)

    return (
        f"Mozilla/5.0 ({device}) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_version}.0.0.{build_number} Safari/537.36"
    )

def get_proxy_string(proxy_port: int = os.environ.get("PROXY_PORT")):
    # socks5h://54595891-zone-custom-region-UA:USS6ATGn@eu.proxys5.net:6200
    # 60d0e3db386eef0527a3:c816dd2e026cafdf@gw.dataimpulse.com:824
    proxy_port = 824
    proxy_host = "gw.dataimpulse.com"
    proxy_user = "60d0e3db386eef0527a3"
    proxy_pass = "c816dd2e026cafdf"
    return f"socks5://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"

def get_random_sec_ch_ua():
    chrome_version = random.randint(125, 130)
    return (
        f'"Chromium";v="{chrome_version}", '
        f'"Google Chrome";v="{chrome_version}", '
        f'"Not?A_Brand";v="99"'
    )

def check_global_items_ids(account_id: int):
    for item_id in GLOBAL_ITEMS_IDS_ACCOUNTS[account_id]:
        for account_id_glob, item_ids in GLOBAL_ITEMS_IDS_ACCOUNTS.items():
            if item_id in item_ids and account_id_glob != account_id:
                GLOBAL_ITEMS_IDS_ACCOUNTS[account_id].remove(item_id)
    GLOBAL_ITEMS_IDS_ACCOUNTS[account_id] = list(set(GLOBAL_ITEMS_IDS_ACCOUNTS[account_id]))

def extract_ids_with_typename(html: str):
    try:
        pattern = r'"__typename":"GroupCommerceProductItem","id":"(\d+)"'
        
        matches = re.findall(pattern, html)
        
        if not matches:
            logger.error("❌ No 'id' found with corresponding '__typename': 'GroupCommerceProductItem'")
            return False

        return matches
    except Exception as e:
        logger.error(f"❌ Error extracting ID with typename 'GroupCommerceProductItem': {e}")
        return False

def extract_has_next_page(html: str):
    try:
        has_next_page_pattern = r'"has_next_page"\s*:\s*(true|false)'
        match = re.search(has_next_page_pattern, html)

        if match:
            has_next_page = match.group(1)
            return has_next_page
        else:
            print("❌ No 'has_next_page' found")
            return False
    except Exception as e:
        print(f"❌ Error parsing: {e}")
        return False

def parse_page_info(html: str):
    try:
        page_info_pattern = r'"page_info":\s*{'
        page_info_start = re.search(page_info_pattern, html)

        if not page_info_start:
            logger.error("❌ No 'page_info' found")
            return False, None
        
        start = page_info_start.end() - 1
        brace_level = 0
        page_info_str = ""
        
        for i in range(start, len(html)):
            char = html[i]
            if char == '{':
                brace_level += 1
            elif char == '}':
                brace_level -= 1

            page_info_str += char
            
            if brace_level == 0:
                break
        else:
            logger.error("❌ Cannot find closing brace for 'page_info'")
            return False, None

        page_info_str = page_info_str.replace(r'\\"', '"')
        page_info_str = page_info_str.replace(r'\\\\', '\\')
        page_info_str = page_info_str.replace('\\', '')

        end_cursor_pattern = r'"end_cursor":\s*"{'
        end_cursor_start = re.search(end_cursor_pattern, page_info_str)
        
        if end_cursor_start:
            start_cursor = end_cursor_start.end() - 1
            brace_level = 0
            end_cursor_str = ""
            
            for i in range(start_cursor, len(page_info_str)):
                char = page_info_str[i]
                if char == '{':
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1

                end_cursor_str += char
                
                if brace_level == 0:
                    break
            else:
                logger.error("❌ Cannot find closing brace for 'end_cursor'")
                return False, None

            result = extract_has_next_page(page_info_str)
            if result == 'true':
                result = True
            else:
                result = False

            return result, end_cursor_str
        else:
            logger.error("❌ No 'end_cursor' found")
            return False
    except Exception as e:
        logger.error(f"❌ Error parsing page_info: {e}")
        return False, None


class FaceBook:
    def __init__(self):
        self.url_fb_category = "https://www.facebook.com/marketplace/category/search/?"
        self.url_fb_search = "https://www.facebook.com/marketplace/0/search/?"

    async def fetch(self, session: httpx.AsyncClient, url, headers, method="GET",params=None, data=None, json=None, content=None, follow_redirects=False):
        # headers["user-agent"] = get_random_user_agent()
        # headers["sec-ch-ua"] = get_random_sec_ch_ua()

        for _ in range(5):
            try:
                if method == "GET":
                    if params:
                        response = await session.get(url, headers=headers, params=params, follow_redirects=follow_redirects)  
                    else:
                        response = await session.get(url, headers=headers, follow_redirects=follow_redirects)
                elif method == "POST":
                    if data:
                        response = await session.post(url, headers=headers, data=data, follow_redirects=follow_redirects)
                    elif json:
                        response = await session.post(url, headers=headers, json=json, follow_redirects=follow_redirects)
                    elif content:
                        response = await session.post(url, headers=headers, content=content, follow_redirects=follow_redirects)
                    else:
                        response = await session.post(url, headers=headers, follow_redirects=follow_redirects)                       
                if response.status_code // 100 == 2  or response.status_code // 100 == 3 or response.status_code==401:
                    return response

                raise Exception(f"Error fetching {url}: {response.status_code}")
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue
            
    async def parse_adv(self, session: httpx.AsyncClient, headers: dict, data: dict, count: int, account_id: int, html: str) -> bool:
        data['dpr'] = '1'
        data['__a'] = '1'
        try:
            tracking_pattern = r'"end_cursor"\s*:\s*"((?:\\.|[^"\\])*)"'
            params_obj = None

            matches = re.findall(tracking_pattern, html)
            if not matches:
                logger.error("❌ No tracking JSON found")
                return False

            for i, raw in enumerate(matches, 1):
                try:
                    json_str = bytes(raw, "utf-8").decode("unicode_escape")
                    tracking_data = json.loads(json_str)
                    cursor_obj = tracking_data
                    break
                except Exception as e:
                    logger.error(f"❌ Could not decode JSON: {e}")
                    continue

            params_start = re.search(r'"params"\s*:\s*\{', html)
            if not params_start:
                logger.error("not found params")
                return False

            start = params_start.end() - 1
            brace_level = 0

            for i in range(start, len(html)):
                if html[i] == '{':
                    brace_level += 1
                elif html[i] == '}':
                    brace_level -= 1
                    if brace_level == 0:
                        json_str = html[start:i + 1]
                        break
            else:
                logger.error("not found params")
                return False

            try:
                tracking_data = json.loads(json_str)
            except Exception as e:
                logger.error(f"Error parsing JSON: {e}")
                return False

            params_obj = tracking_data
            data.update({'fb_api_caller_class':'RelayModern','fb_api_req_friendly_name':'CometMarketplaceSearchContentPaginationQuery','variables': json.dumps({"count":24,"scale":1,"cursor":json.dumps(cursor_obj),"params": json.dumps(params_obj)}),'server_timestamps':True,'doc_id':'9220222444737099'})
            
            resp = await self.fetch(session, 'https://web.facebook.com/api/graphql/', headers, data=data, method="POST")
            resp = resp.json()
            for position in resp['data']['marketplace_search']['feed_units']['edges']:
                if position['node']['__typename'] == 'MarketplaceFeedListingStoryObject':
                    item_id = position['node']['listing']['id']
                    GLOBAL_ITEMS_IDS_ACCOUNTS[account_id].append(item_id)

            check_global_items_ids(account_id)
            cursor_obj = resp['data']['marketplace_search']['feed_units']['page_info']['end_cursor']
            while len(GLOBAL_ITEMS_IDS_ACCOUNTS[account_id]) < count:
                data.update({'fb_api_caller_class':'RelayModern','fb_api_req_friendly_name':'CometMarketplaceSearchContentPaginationQuery','variables': json.dumps({"count":24,"scale":1,"cursor":cursor_obj,"params": json.dumps(params_obj)}),'server_timestamps':True,'doc_id':'9220222444737099'})
                resp = await self.fetch(session, 'https://web.facebook.com/api/graphql/', headers, data=data, method="POST")
                try:
                    resp = resp.json()
                    if resp.get('errors'):
                        logger.error(f"Error in response: {resp['errors']}")
                        return False
                    for position in resp['data']['marketplace_search']['feed_units']['edges']:
                        if position['node']['__typename'] == 'MarketplaceFeedListingStoryObject':
                            item_id = position['node']['listing']['id']
                            GLOBAL_ITEMS_IDS_ACCOUNTS[account_id].append(item_id)
                    cursor_obj = resp['data']['marketplace_search']['feed_units']['page_info']['end_cursor']
                    if not resp['data']['marketplace_search']['feed_units']['page_info']['has_next_page']:
                        break
                except:
                    item_ids = extract_ids_with_typename(resp.text)
                    for item_id in item_ids:
                        GLOBAL_ITEMS_IDS_ACCOUNTS[account_id].append(item_id)

                    next_page, cursor_obj = parse_page_info(resp.text)
                    if not next_page:
                        break
                    
                    if not cursor_obj:
                        logger.error("❌ Failed to find 'end_cursor'")
                        return True

                if len(GLOBAL_ITEMS_IDS_ACCOUNTS[account_id]) >= count:
                    check_global_items_ids(account_id)
                    await self.clean_old_links(account_id)
            return True
        except Exception as e:
            logger.error(f"Error in ScrapDetail: {e}")
            return False

    async def clean_old_links(self, account_id):
        products =  await get_products()
        for product in products:
            if product["id"] in GLOBAL_ITEMS_IDS_ACCOUNTS[account_id]:
                GLOBAL_ITEMS_IDS_ACCOUNTS[account_id].remove(product["id"])

    async def login_by_cookies(self, account: dict) -> bool:
        headers = HEADERS.copy()
        headers["user-agent"] = account['user_agent']

        cookies_dict = {
            key.strip(): value.strip()
            for key, value in (item.split("=", 1) for item in account['cookie'].split(";") if "=" in item)
        }

        async with httpx.AsyncClient(cookies=cookies_dict, proxy=f"socks5://{account['proxy_url']}") as session:
            try:
                response = await self.fetch(session, 'https://www.facebook.com/profile.php', headers=headers, follow_redirects=True)
                req_text = response.text

                id = re.search(r'"actorID":"(.*?)"', req_text).group(1)
                nm = re.search(r'"NAME":"(.*?)"', req_text).group(1)

                if not int(id) or not nm:
                    logger.error(f"Error in LoginCookie2: {id} {nm}")
                    return False
            except Exception as e:
                logger.error(f"Error in LoginCookie2: {e}")
                return False
            
        return await self.change_radius(account, 500)
        
    async def get_geolocation_id(self, session, headers, data, query, html) -> None:
        try:
            pattern = r'"latitude"\s*:\s*(-?[0-9.]+)\s*,\s*"longitude"\s*:\s*(-?[0-9.]+)'

            match = re.search(pattern, html)

            if match:
                latitude = float(match.group(1))
                longitude = float(match.group(2))
            else:
                logger.error("Coordinates not found in the response")
                
            new_data = {
                'latitude': latitude,
                'longitude': longitude,
            }

            variables = {
                "params":{
                    "caller":"MARKETPLACE",
                    "country_filter":None,
                    "integration_strategy":"STRING_MATCH",
                    "page_category":["CITY","SUBCITY","NEIGHBORHOOD","POSTAL_CODE"],
                    "query": query,
                    "search_type":"PLACE_TYPEAHEAD",
                    "viewer_coordinates":json.dumps(new_data),
                }
            }
            data.update({'fb_api_caller_class':'RelayModern','fb_api_req_friendly_name':'MarketplaceSearchAddressDataSourceQuery','variables': json.dumps(variables),'server_timestamps':True,'doc_id':'7321914954515895'})
            # pos = await session.post('https://web.facebook.com/api/graphql/', data=data)
            pos = await self.fetch(session, 'https://web.facebook.com/api/graphql/', headers, data=data, method="POST")
            pos = pos.json()
            for position in pos['data']['city_street_search']['street_results']['edges']:
                return position['node']['page']['id']
            logger.error("Geolocation ID not found")
            return None
        except Exception as e:
            logger.error(f"Error in get_geolocation_id: {e}")
            return "error"
        
    async def change_radius_location(self, session: httpx.AsyncClient, headers: dict, data: dict, radius: int) -> bool:
        try:
            variables= {"input": json.dumps({
                "browse_radius": radius,
                "actor_id": data['__user'],
                "client_mutation_id": "2"})
            }
            data.update({'fb_api_caller_class':'RelayModern','fb_api_req_friendly_name':'CometMarketplaceSetBrowseRadiusMutation','variables': json.dumps(variables),'server_timestamps':True,'doc_id':'4948757418538143'})
            response = await self.fetch(session, 'https://web.facebook.com/api/graphql/', headers, data=data, method="POST", follow_redirects=True)
            try:
                pos = response.json()
                if pos['data']['marketplace_set_browse_radius']['viewer']['marketplace_settings']['browse_radius']:
                    logger.info("Radius location changed")
                    return True
                else:
                    logger.error("Radius location not changed")
                    return False
            except:
                logger.error("Error parsing response")
        except Exception as e:
            logger.error(f"Error in Execute: {e}")
            return
        
    async def send_message(self, session, headers, data, message, html, account_id) -> bool:
        commerce_rank_obj = {}
        try:
            tracking_pattern = r'"tracking"\s*:\s*"((?:\\.|[^"\\])*)"'

            matches = re.findall(tracking_pattern, html)
            if not matches:
                logger.error("No tracking JSON found")
                return
                
            for i, raw in enumerate(matches, 1):
                try:
                    json_str = bytes(raw, "utf-8").decode("unicode_escape")
                    tracking_data = json.loads(json_str)
                    
                    if "commerce_rank_obj" in tracking_data:
                        commerce_rank_obj = json.loads(tracking_data["commerce_rank_obj"])
                        break
                except Exception as e:
                    logger.error(f"Could not decode JSON: {e}")
                    continue

            if not commerce_rank_obj:
                logger.error("Commerce rank object not found")
                return False

            commerce_rank_obj_str = tracking_data['commerce_rank_obj']
            commerce_rank_obj = json.loads(commerce_rank_obj_str)


            listing_id = re.search('"listing_id":"(.*?)"',str(html)).group(1)
            Vir = {
                "qid":tracking_data['qid'],
                "mf_story_key":tracking_data['mf_story_key'],
                "commerce_rank_obj": {
                "target_id":commerce_rank_obj['target_id'],
                "target_type":commerce_rank_obj['target_type'],
                "primary_position":commerce_rank_obj['primary_position'],
                "ranking_signature":commerce_rank_obj['ranking_signature'],
                "commerce_channel":commerce_rank_obj['commerce_channel'],
                "value":commerce_rank_obj['value'],
                "candidate_retrieval_source_map": json.dumps(commerce_rank_obj['candidate_retrieval_source_map'])
            }
            }
            Var = {
                "input":{
                    "client_mutation_id":"2",
                    "actor_id":data['__user'],
                    "listing_id": listing_id,
                    "is_customized_message": False,
                    "message": message,
                    "attribution_id_v2":"CometMarketplacePermalinkRoot.react,comet.marketplace.item,unexpected,1742920360306,728915,1606854132932955,,;CometMarketplaceSearchContentContainer.react,comet.marketplace.category,via_cold_start,1742920358085,75377,1606854132932955,494,997455369115440",
                    "tracking": json.dumps(Vir),
                    "referral_surface":"category_feed",
                    "surface":"product_details",
                    "ui_component":"contact_seller_button",
                    }}
            data.update({'fb_api_caller_class':'RelayModern','fb_api_req_friendly_name':'CometMarketplaceMessageSellerMutation','variables':json.dumps(Var),'server_timestamps':True,'doc_id':'4861194384003324'})
            resp = await self.fetch(session, 'https://web.facebook.com/api/graphql/', headers, data=data, method="POST")
            if '"data":{"marketplace_message_seller":{"success":true' in str(resp.text):
                logger.success(f"Message sent successfully to item {listing_id} from account {account_id}") 
                return True
            logger.error(f"Error sending message: {resp.text} for item {listing_id} from account {account_id}")
            return False
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            return False
        
    async def spam_marketplace(self, bot: Bot, account):
        try:
            headers = HEADERS.copy()
            headers["user-agent"] = account['user_agent']
            
            cookies_dict = {
                key.strip(): value.strip()
                for key, value in (item.split("=", 1) for item in account["cookie"].split(";") if "=" in item)
            }

            async with httpx.AsyncClient(cookies=cookies_dict, proxy=f"socks5://{account['proxy_url']}") as session:
                url = "https://www.facebook.com/marketplace/category/search/?query=vehicles"
                if account["category_link"]:
                    if len(account["category_link"].split("=")) > 1:
                        query = account["category_link"].split("=")[1]
                    else:
                        query = account["category_link"].split("/")[-1]
                    
                    if account["geolocation_id"]:
                        url = self.url_fb_search.replace("0", str(account["geolocation_id"])) + f"query={query}"
                    else:
                        url = self.url_fb_category + f"query={query}"
                        
                if account["time_filter_spam_id"]:
                    if account["time_filter_spam_id"] in[1, 2, 3, 4, 5, 6]:
                        url += "&daysSinceListed=1"
                    elif account["time_filter_spam_id"] == 7:
                        url += "&daysSinceListed=7"
                    elif account["time_filter_spam_id"] == 8:
                        url += "&daysSinceListed=30"

                response = await self.fetch(session, url, headers=headers, follow_redirects=True)
                if response.status_code != 200:
                    logger.error(f"Error fetching category link: {response.status_code}")
                    return

                html = response.text
                parse_adv_html(html, account["id"])
                data = get_data(html)
                account_id = account["id"]

                check_global_items_ids(account_id)
                await self.clean_old_links(account_id)
                
                if len(GLOBAL_ITEMS_IDS_ACCOUNTS[account_id]) < account["count_spam"]:
                    if not await self.parse_adv(session, headers, data, account["count_spam"], account["id"], html):
                        await set_is_blocked(account_id, True)
                        logger.warning(f"Account {account['id']} is blocked")
                        await bot.send_message(
                            chat_id=account["user_id"],
                            text=f"Account {account['id']} is blocked"
                        )
                        return
                
                expected_success = account["count_spam"]
                real_success = 0
                count = 0
                for item_id in GLOBAL_ITEMS_IDS_ACCOUNTS[account["id"]]:
                    account = await get_account(account["id"])
                    if account["is_blocked"]:
                        break
                    
                    item_url = f"https://www.facebook.com/marketplace/item/{item_id}/"
                    response = await self.fetch(session, item_url, headers=headers, follow_redirects=True)
                    if not response:
                        logger.error(f"Error fetching item link: {item_url}")
                        continue
                    html = response.text
                    data = get_data(html)
                    if not data.get("__user"):
                        data['__user'] = cookies_dict['c_user']

                    if await self.send_message(session, headers, data, account["text_spam"], html, account["id"]):
                        await create_product(item_id)
                        real_success += 1

                    count += 1
                    if count >= expected_success:
                        del GLOBAL_ITEMS_IDS_ACCOUNTS[account["id"]]
                        break
                    await asyncio.sleep(account["rate_limit"])
                
                if real_success == 0:
                    await set_is_blocked(account["id"], True)
                    logger.warning(f"Account {account['id']} is blocked")
                    await bot.send_message(
                        chat_id=account["user_id"],
                        text=f"Account {account['id']} is blocked"
                    )

                logger.info(f"Spam completed for account {account['id']}: expected {expected_success}, sent {real_success}")
                await bot.send_message(
                    chat_id=account["user_id"],
                    text=f"Spam completed for account {account['id']}: expected {expected_success}, sent {real_success}"
                )
        except Exception as e:
            logger.error(f"Error in spam_marketplace: {e}")

    async def change_radius(self, account: dict, radius: int) -> bool:
        try:
            headers = HEADERS.copy()
            headers["user-agent"] = account['user_agent']
            
            cookies_dict = {
                key.strip(): value.strip()
                for key, value in (item.split("=", 1) for item in account["cookie"].split(";") if "=" in item)
            }

            async with httpx.AsyncClient(cookies=cookies_dict, proxy=f"socks5://{account['proxy_url']}") as session:
                url = "https://www.facebook.com/marketplace/category/search/?query=vehicles"
                response = await self.fetch(session, url, headers=headers, follow_redirects=True)
                if response.status_code != 200:
                    logger.error(f"Error fetching category link: {response.status_code}")
                    return
                data = get_data(response.text)
                if not data:
                    logger.error("Error fetching data")
                    return

                return await self.change_radius_location(session, headers, data, radius)
        except Exception as e:
            logger.error(f"Error in change_radius: {e}")
            
    async def change_geolocation(self, account: dict, query: str) -> bool:
        try:
            headers = HEADERS.copy()
            headers["user-agent"] = account['user_agent']
            
            cookies_dict = {
                key.strip(): value.strip()
                for key, value in (item.split("=", 1) for item in account["cookie"].split(";") if "=" in item)
            }

            async with httpx.AsyncClient(cookies=cookies_dict, proxy=f"socks5://{account['proxy_url']}") as session:
                url = "https://www.facebook.com/marketplace/category/search/?query=vehicles"
                response = await self.fetch(session, url, headers=headers, follow_redirects=True)
                if response.status_code != 200:
                    logger.error(f"Error fetching category link: {response.status_code}")
                    return
                html = response.text
                data = get_data(html)
                if not data:
                    logger.error("Error fetching data")
                    return

                return await self.get_geolocation_id(session, headers, data, query, html)
        except Exception as e:
            logger.error(f"Error in change_radius: {e}")
