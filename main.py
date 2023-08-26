# Made by chareou (roblox) lovingsosa (disccord)
# edited by .ftgs (DONT KILLme)

# https://discord.gg/X5QpjtmYW3 Cloud Discord Server

try:
    import os, requests, json, time, colorama, traceback, threading, random, sys, asyncio
except ImportError:
    os.system("pip install requests colorama")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36", "Accept-Encoding": "gzip", "Content-Type": "application/json; charset=utf-8"}

config = json.load(open("settings.json", "r"))

class Snipe:
    
    def __init__(self) -> None:
        self.VERSION = "1.0.0"
        self.session = requests.Session()
        self.ready = False
        self.only_new = config["misc"]["only_new"]
        self.accounts = {config["accounts"]["main_account"][-4:]: {"name": None, "id": 0, "cookie": config["accounts"]["main_account"], "auth": None, "owned_bundles": [], "owned_heads": []}}

        for cookie in config["accounts"]["alt_accounts"]:
            if cookie:
                self.accounts[cookie[-4:]] = {"name": None, "id": 0, "cookie": cookie, "auth": None, "owned_bundles": [], "owned_heads": []}

        self.verify_cookies()
        threading.Thread(target=self.auto_updater).start()
        threading.Thread(target=self.version_updater).start()

        while not self.ready:
            time.sleep(1)
            
        print(f"[{colorama.Fore.GREEN}SUCCESS{colorama.Fore.RESET}] - CloudBundle Sniper Started{colorama.Fore.RESET}")

        if config["webhook"]["enabled"]:
            self.webhook_url = config["webhook"]["url"]

        if config["misc"]["bundles"]:
            threading.Thread(target=self.get_free_bundles).start()

        if config["misc"]["heads"]:
            threading.Thread(target=self.get_free_heads).start()

    def version_updater(self):
        response = self.session.get("https://raw.githubusercontent.com/AlikSusFootages/cloudBundle/main/version")
        if response.status_code == 200:
            version = response.json()
            if version == self.VERSION:
                print(f"[{colorama.Fore.GREEN}SUCCESS{colorama.Fore.RESET}] - Version is new! {response.text}{colorama.Fore.RESET}")
            else:
                print(f"[{colorama.Fore.YELLOW}CHECK{colorama.Fore.RESET}] - Current version: {self.VERSION}{colorama.Fore.RESET}")
                time.sleep(1)
                print(f"[{colorama.Fore.YELLOW}VERSION{colorama.Fore.RESET}] - New version: {version['version']}")

    def verify_cookies(self):
        for cookie, details in self.accounts.items():
            response = self.session.get(
                "https://users.roblox.com/v1/users/authenticated",
                headers={"Cookie": f'.ROBLOSECURITY={details["cookie"]}'},
            )
            if response.status_code == 200:
                json_response = response.json()
                self.accounts[cookie]["id"] = json_response.get("id")
                self.accounts[cookie]["name"] = json_response.get("name")
            else:
                print(f"[{colorama.Fore.RED}ERROR{colorama.Fore.RESET}] - Invalid cookie or ratelimit try again in a minute {response.text}{colorama.Fore.RESET}")
                sys.exit()

    def get_owned(self):
        if config["misc"]["bundles"]:
            for account in self.accounts:
                with requests.Session() as session:
                    cursor = ""
                    while cursor is not None:
                        response = session.get(f'https://catalog.roblox.com/v1/users/{self.accounts[account]["id"]}/bundles/1?limit=100&nextPageCursor=&sortOrder=Desc&cursor={cursor}', headers={"Cookie": f'.ROBLOSECURITY={self.accounts[account]["cookie"]}'})
                        if response.status_code == 200:
                            json_response = response.json()
                            cursor = json_response["nextPageCursor"]
                            for item in json_response["data"]:
                                if (item["id"] not in self.accounts[account]["owned_bundles"]):
                                    self.accounts[account]["owned_bundles"].append(item["id"])
                        else:
                            time.sleep(2)

        if config["misc"]["heads"]:
            for account in self.accounts:
                with requests.Session() as session:
                    cursor = ""
                    while cursor is not None:
                        response = session.get(f'https://catalog.roblox.com/v1/users/{self.accounts[account]["id"]}/bundles/4?limit=100&nextPageCursor=&sortOrder=Desc&cursor={cursor}',headers={"Cookie": f'.ROBLOSECURITY={self.accounts[account]["cookie"]}'})
                        if response.status_code == 200:
                            json_response = response.json()
                            cursor = json_response["nextPageCursor"]
                            for item in json_response["data"]:
                                if (item["id"] not in self.accounts[account]["owned_heads"]):
                                    self.accounts[account]["owned_heads"].append(item["id"])
                        else:
                            time.sleep(2)

    def send_webhook(self, name, user, bundle_id, price):
        if config["webhook"]["enabled"]:
            data = {"content": None, "embeds": [{"title": f"{user} bought {name}", "description": f"Price: {price}", "url": f"https://roblox.com/bundles/{bundle_id}", "color": 0x2ecc71, "thumbnail": {"url": None}, "footer": {"text": f"v{self.VERSION} | Thanks for using!"}, "author": {"name": "CloudBundle Sniper", "icon_url": "https://cdn.discordapp.com/attachments/1133768987059163247/1135692497297883307/168_20230731215620.png", "url": "https://discord.gg/X5QpjtmYW3"}}]}
            try:
                thumbnail = self.session.get(f"https://thumbnails.roblox.com/v1/bundles/thumbnails?bundleIds={bundle_id}&size=150x150&format=Png&isCircular=false")
                if thumbnail.status_code == 200:
                    thumbnail = thumbnail.json()["data"][0]["imageUrl"]
                else:
                    thumbnail = None

                data["embeds"][0]["thumbnail"]["url"] = thumbnail
                self.session.post(self.webhook_url, json=data)
            except Exception:
                pass
                
    def __get_thumbnail(self, id):
        thumbnail = self.session.get(f"https://thumbnails.roblox.com/v1/bundles/thumbnails?bundleIds={id}&size=150x150&format=Png&isCircular=false")
        if thumbnail.status_code == 200:
            thumbnail = thumbnail.json()["data"][0]["imageUrl"]
        else:
            thumbnail = None
        
        return thumbnail
                
    def send_log_global(self, user, name, price, id):
        thumbnail = self.__get_thumbnail(id)
        self.accname = user
        if config['misc']["globallogs"]['anonymous'] == True:
            self.accname = "Anonymous"
        headers = f'[{{"accname": "{self.accname}", "name": "{name}", "price": "{price}", "bought_from": "CloudBundle Sniper", "iconUrl": "{thumbnail}", "urlItem": "https://www.roblox.com/bundles/{id}/CloudGlobalLogs", "itemType": "Bundle"}}]'
        data = {"headers": headers}
        response = requests.post("https://globallogs.aliksis.repl.co", data=data)

    def fetch_bundle_data(self, cursor):
        url = "https://catalog.roblox.com/v1/search/items?limit=120&category=Characters&sortType=3&maxPrice=0&salesTypeFilter=1"
        try:
            response = self.session.get(f"{url}&cursor={cursor}" if cursor is not None else url, cookies={".ROBLOSECURITY": self.accounts.get(config["accounts"]["main_account"][-4:])["cookie"]}, headers=HEADERS)
            return response
        except:
            return

    def fetch_head_data(self, cursor):
        url = "https://catalog.roblox.com/v2/search/items/details?sortType=3&category=BodyParts&limit=120&maxPrice=0&salesTypeFilter=1"
        try:
            response = self.session.get(f"{url}&cursor={cursor}" if cursor is not None else url, cookies={".ROBLOSECURITY": self.accounts.get(config["accounts"]["main_account"][-4:])["cookie"]}, headers=HEADERS)
            return response
        except:
            return

    def get_free_bundles(self):
        current_cursor = ""

        if self.only_new == True:
            while current_cursor is not None:
                response = self.fetch_bundle_data(current_cursor)
                if response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            self.accounts[account]["owned_bundles"].append(item["id"])
                time.sleep(0.5)

        while True:
            try:
                response = self.fetch_bundle_data(current_cursor)
                if response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            if (item["id"] not in self.accounts[account]["owned_bundles"]):
                                extra_info = self.session.get(f'https://catalog.roblox.com/v1/bundles/{item["id"]}/details', cookies={".ROBLOSECURITY": config["accounts"]["main_account"][-4:]})
                                if extra_info.status_code == 200:
                                    extra_json = extra_info.json()
                                    self.buy(extra_json["product"]["id"], extra_json["creator"]["id"], account, extra_json["id"], extra_json["name"], "bundle", extra_json["product"]["priceInRobux"])
                                    time.sleep(0.5)
                time.sleep(2)
            except Exception as error:
                print(f"[{colorama.Fore.RED}ERROR{colorama.Fore.RESET}]:\n {traceback.format_exc()}")

    def get_free_heads(self):
        current_cursor = ""

        if self.only_new == True:
            while current_cursor is not None:
                response = self.fetch_head_data(current_cursor)
                if response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            if (item["id"] not in self.accounts[account]["owned_heads"] and item.get("itemType") == "Bundle" and item.get("bundleType") == 4):
                                self.accounts[account]["owned_heads"].append(item["id"])
                time.sleep(0.5)

        while True:
            try:
                response = self.fetch_head_data(current_cursor)
                if response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            if (item["id"] not in self.accounts[account]["owned_heads"] and item.get("itemType") == "Bundle" and item.get("bundleType") == 4):
                                extra_info = self.session.get(f'https://catalog.roblox.com/v1/bundles/{item["id"]}/details', cookies={".ROBLOSECURITY": config["accounts"]["main_account"][-4:]})
                                if extra_info.status_code == 200:
                                    extra_json = extra_info.json()
                                    self.buy(extra_json["product"]["id"], extra_json["creator"]["id"], account, extra_json["id"], extra_json["name"], "head", extra_json["product"]["priceInRobux"])
                                    time.sleep(0.5)
                time.sleep(2)
            except Exception as error:
                print(f"[{colorama.Fore.RED}ERROR{colorama.Fore.RESET}]:\n {traceback.format_exc()}")

    def refresh_cookies(self):
        for cookie, details in self.accounts.items():
            try:
                response = self.session.post("https://friends.roblox.com/v1/users/1/request-friendship", headers={"Cookie": f'.ROBLOSECURITY={details["cookie"]}'})
                if response.headers.get("x-csrf-token"):
                    self.accounts[cookie]["auth"] = response.headers["x-csrf-token"]
                else:
                    raise Exception

            except Exception:
                input(f"> 2 Invalid cookie ending in {cookie}")
                exit(0)

    def auto_updater(self):
        self.get_owned()
        while True:
            self.refresh_cookies()
            self.ready = True
            time.sleep(240)

    def buy(self, productid, sellerid, account, id_, name, type_, price):
        payload = {"expectedCurrency": 1, "expectedPrice": 0, "expectedSellerId": sellerid}

        buy_headers = HEADERS.copy()
        buy_headers["x-csrf-token"] = self.accounts[account]["auth"]
        while True:
            try:
                response = self.session.post(f"https://economy.roblox.com/v1/purchases/products/{productid}", json=payload, cookies={".ROBLOSECURITY": self.accounts[account]["cookie"]}, headers=buy_headers)
                if response.status_code == 200:
                    status = response.json().get("statusCode", 690)
                    if status == 500:
                        print(f"[{colorama.Fore.RED}ERROR{colorama.Fore.RESET}] Something went wrong: {response.json()['errorMsg']}")
                        if response.json()["errorMsg"] == "You already own this item.":
                            if type_ == "bundle":
                                self.accounts[account]["owned_bundles"].append(id_)
                            else:
                                self.accounts[account]["owned_heads"].append(id_)
                            break
                        elif response.json()["errorMsg"] == "This item has changed price. Please try again.":
                            if type_ == "bundle":
                                self.accounts[account]["owned_bundles"].append(id_)
                            else:
                                self.accounts[account]["owned_heads"].append(id_)
                            break
                    elif status == 690:
                        print(f"[{colorama.Fore.GREEN}BOUGHT{colorama.Fore.RESET}] - Successfully bought {name} ({type_}) on {self.accounts[account]['name']}")
                        if type_ == "bundle":
                            self.accounts[account]["owned_bundles"].append(id_)
                        else:
                            self.accounts[account]["owned_heads"].append(id_)
                        threading.Thread(target=self.send_webhook(name, self.accounts[account]["name"], id_, price)).start()
                        threading.Thread(target=self.send_log_global(self.accounts[account]["name"], name, price, id_)).start()
                        break
                    else:
                        break
                elif response.status_code == 403:
                    if "Too many requests" in response.text:
                        print(f"[{colorama.Fore.YELLOW}RATELIMIT{colorama.Fore.RESET}] Waiting a minute to buy {name} on {self.accounts[account]['name']}")
                        time.sleep(60)
                    else:
                        if "Token Validation Failed" in response.text:
                            print(f"[{colorama.Fore.YELLOW}XCSRF-TOKEN{colorama.Fore.RESET}]Refreshing auth token")
                            self.refresh_cookies()
                            buy_headers["x-csrf-token"] = self.accounts[account]["auth"]
                            time.sleep(1)
            except Exception:
                print(f"[{colorama.Fore.RED}ERROR{colorama.Fore.RESET}]:\n {traceback.format_exc()}")

if __name__ == "__main__":
    Snipe()
