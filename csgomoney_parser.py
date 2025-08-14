import asyncio
import json
import time
import logging
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')
from telegram.ext import Application
from bs4 import BeautifulSoup
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


with open("skins.json", "r", encoding="utf-8") as f:
    skins_data = json.load(f)

выгода = []


chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--log-level=3")


skin_to_url = {
    "Glock-18 | Water Elemental (Field-Tested)": "https://www.c5game.com/en/csgo/22721/Glock-18%20%7C%20Water%20Elemental/sell?minWear&maxWear=0.16",
    "M4A1-S | Hyper Beast (Field-Tested)": "https://www.c5game.com/en/csgo/22557/M4A1-S%20%7C%20Hyper%20Beast/sell?minWear=0.15&maxWear=0.18",
    "M4A1-S | Hyper Beast (Field-Tested)": "https://www.c5game.com/en/csgo/22557/M4A1-S%20%7C%20Hyper%20Beast/sell?minWear=0.18&maxWear=0.21",
    "M4A1-S | Hyper Beast (Minimal Wear)": "https://www.c5game.com/en/csgo/23705/M4A1-S%20%7C%20Hyper%20Beast/sell?minWear&maxWear=0.09",
    "AWP | Wildfire (Factory New)": "https://www.c5game.com/en/csgo/553485855/AWP%20%7C%20Wildfire%20(Factory%20New)/sell?minWear=&maxWear=0.02",
    "M4A4 | 龍王 (Dragon King) (Field-Tested)": "https://www.c5game.com/en/csgo/22973/M4A4%20%7C%20%E9%BE%8D%E7%8E%8B/sell?minWear&maxWear=0.17",
    "P250 | Muertos (Factory New)": "https://www.c5game.com/en/csgo/24033/P250%20%7C%20Muertos/sell?minWear&maxWear=0.02",
    "UMP-45 | Blaze (Factory New)": "https://www.c5game.com/en/csgo/25002/UMP-45%20%7C%20Blaze/sell?minWear=0&maxWear=0.01",
    "AK-47 | Nightwish (Factory New)": "https://www.c5game.com/en/csgo/958661081649799168/AK-47%20%7C%20Nightwish%20(Factory%20New)/sell?minWear=0&maxWear=0.01",
    "AK-47 | Nightwish (Factory New)": "https://www.c5game.com/en/csgo/958661081649799168/AK-47%20%7C%20Nightwish%20(Factory%20New)/sell?minWear=0.01&maxWear=0.02",
    "Desert Eagle | Conspiracy (Factory New)": "https://www.c5game.com/en/csgo/23964/Desert%20Eagle%20%7C%20Conspiracy%20(Factory%20New)/sell?sort=0&minWear=0&maxWear=0.01",
    "Desert Eagle | Conspiracy (Factory New)": "https://www.c5game.com/en/csgo/23964/Desert%20Eagle%20%7C%20Conspiracy%20(Factory%20New)/sell?sort=0&minWear=0&maxWear=0.02",
    "Desert Eagle | Crimson Web (Minimal Wear)": "https://www.c5game.com/en/csgo/23244/Desert%20Eagle%20%7C%20Crimson%20Web/sell?minWear=0.07&maxWear=0.08",
    "Desert Eagle | Crimson Web (Minimal Wear)": "https://www.c5game.com/en/csgo/23244/Desert%20Eagle%20%7C%20Crimson%20Web/sell?minWear=0.08&maxWear=0.09",
    "Glock-18 | Bullet Queen (Factory New)": "https://www.c5game.com/en/csgo/553489879/Glock-18%20%7C%20Bullet%20Queen/sell?minWear=0&maxWear=0.01",
    "MAC-10 | Neon Rider (Factory New)": "https://www.c5game.com/en/csgo/24435/MAC-10%20%7C%20Neon%20Rider%20(Factory%20New)/sell?minWear=&maxWear=0.02",
    "USP-S | Printstream (Factory New)": "https://www.c5game.com/en/csgo/1017617021485346816/USP-S%20%7C%20Printstream%20(Factory%20New)/sell?minWear=0&maxWear=0.02",
    "StatTrak™ Desert Eagle | Light Rail (Factory New)": "https://www.c5game.com/en/csgo/553482670/StatTrak%E2%84%A2%20Desert%20Eagle%20%7C%20Light%20Rail%20(Factory%20New)/sell?minWear=0&maxWear=0.01",
    "Glock-18 | Franklin (Factory New)": "https://www.c5game.com/en/csgo/808830880107069440/Glock-18%20%7C%20Franklin%20(Factory%20New)/sell?minWear=0&maxWear=0.01",
    "Desert Eagle | Printstream (Factory New)": "https://www.c5game.com/en/csgo/553491656/Desert%20Eagle%20%7C%20Printstream%20(Factory%20New)/sell?minWear=&maxWear=0.02",
    "StatTrak™ M4A1-S | Chantico's Fire (Factory New)": "https://www.c5game.com/en/csgo/236782611/StatTrak%E2%84%A2%20M4A1-S%20%7C%20Chantico's%20Fire%20(Factory%20New)/sell?minWear=&maxWear=0.02",
    "M4A1-S | Control Panel (Factory New)": "https://www.c5game.com/en/csgo/553479519/M4A1-S%20%7C%20Control%20Panel/sell?minWear=0&maxWear=0.01",
    "P90 | Cold Blooded (Factory New)": "https://www.c5game.com/en/csgo/24393/P90%20%7C%20Cold%20Blooded%20(Factory%20New)/sell?minWear=&maxWear=0.02",
}

def process_url(skin_name, url):
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        skins = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, "on-sale-table-item"))

        def parse_skin(skin_element):
            soup = BeautifulSoup(skin_element.get_attribute("innerHTML"), 'html.parser')
            skin_title = soup.find('img', alt=True)['alt'] if soup.find('img', alt=True) else "Название не найдено"
            abrasion = float(soup.find('div', class_='abrasion-value').text.strip()) if soup.find('div', class_='abrasion-value') else None
            price = float(soup.find(string=lambda t: '\xa5' in t).strip().replace('\xa5', '').replace(',', '')) if soup.find(string=lambda t: '\xa5' in t) else None
            return {"Название": skin_title, "Износ": abrasion, "Цена": price}

        parsed_skins = [parse_skin(skin) for skin in skins]

        for skin in parsed_skins:  
            if skin["Название"] == skin_name:
                print(f"Обрабатываем {skin['Название']} (Износ: {skin['Износ']}, Цена: {skin['Цена']})")

            # Проверка выгодности для Glock-18 | Water Elemental (Field-Tested)
            if skin['Название'] == "Glock-18 | Water Elemental (Field-Tested)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.1509:
                        ratio = 52.5 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.1504, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio  
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1524:
                        ratio = 51 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.1524, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1544:
                        ratio = 49 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.1544, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1555:
                        ratio = 48 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.1555, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1568:
                        ratio = 46.4 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.1568, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1578:
                        ratio = 45.5 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.1578, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    
            # Проверка выгодности для M4A1-S | Hyper Beast (Field-Tested)
            if skin['Название'] == "M4A1-S | Hyper Beast (Field-Tested)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.159:
                        ratio = 245 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1649:
                        ratio = 236 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.168:
                        ratio = 233 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.171:
                        ratio = 228 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.18:
                        ratio = 223 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1855:
                        ratio = 215 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.192:
                        ratio = 208 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.197:
                        ratio = 202 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.200:
                        ratio = 190 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.2025, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.2088:
                        ratio = 199 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.205, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                            # Проверка выгодности для M4A4 | 龍王 (Dragon King) (Field-Tested)
            if skin['Название'] == "M4A4 | 龍王 (Dragon King) (Field-Tested)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.1513:
                        ratio = 93.6 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1525:
                        ratio = 92.5 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1538:
                        ratio = 91.4 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1546:
                        ratio = 90.2 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1556:
                        ratio = 89.8 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1581:
                        ratio = 87.4 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.16:
                        ratio = 86.2 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.163:
                        ratio = 83.7 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)        
                    elif skin['Износ'] < 0.167:
                        ratio = 80 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)            
            # Проверка выгодности для P250 | Muertos (Factory New)
            if skin['Название'] == "P250 | Muertos (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.001:
                        ratio = 186 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.003:
                        ratio = 171 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.009:
                        ratio = 140 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.015:
                        ratio = 114 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.162:
                        ratio = 111 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1645:
                        ratio = 109 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.166:
                        ratio = 105 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.1683:
                        ratio = 100 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                            
            # Проверка выгодности для Desert Eagle | Crimson Web (Minimal Wear)
            if skin['Название'] == "Desert Eagle | Crimson Web (Minimal Wear)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.0733:
                        ratio = 523 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0777:
                        ratio = 487 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.081:
                        ratio = 435 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0825:
                        ratio = 420 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0866:
                        ratio = 375 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.09:
                        ratio = 333 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.092:
                        ratio = 316 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0933:
                        ratio = 310 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
            
                            # Проверка выгодности для UMP-45 | Blaze (Factory New)
            if skin['Название'] == "UMP-45 | Blaze (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.002:
                        ratio = 190 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0032:
                        ratio = 181 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.005:
                        ratio = 158 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.006:
                        ratio = 147 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0070:
                        ratio = 136 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
            #                  # M4A1-S | Hyper Beast (Minimal Wear)
            if skin['Название'] == "M4A1-S | Hyper Beast (Minimal Wear)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.081:
                        ratio = 433 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0823:
                        ratio = 417 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0845:
                        ratio = 405 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0855:
                        ratio = 394 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    # Проверка выгодности для AK-47 | Nightwish (Factory New)
            if skin['Название'] == "AK-47 | Nightwish (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.0015:
                        ratio = 480 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0027:
                        ratio = 465 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0038:
                        ratio = 450 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0046:
                        ratio = 444 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0065:
                        ratio = 435 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.008:
                        ratio = 430 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.01:
                        ratio = 386 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.012:
                        ratio = 415 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.014:
                        ratio = 407 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.016:
                        ratio = 400 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.018:
                        ratio = 394 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                      # Проверка выгодности для Desert Eagle | Conspiracy (Factory New)
            if skin['Название'] == "Desert Eagle | Conspiracy (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.0015:
                        ratio = 140 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0025:
                        ratio = 126 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0040:
                        ratio = 112 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.007:
                        ratio = 103 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0065:
                        ratio = 101 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.011:
                        ratio = 90 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.015:
                        ratio = 82 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.018:
                        ratio = 75 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                          # Проверка выгодности для Glock-18 | Bullet Queen (Factory New)
            if skin['Название'] == "Glock-18 | Bullet Queen (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.0015:
                        ratio = 456 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0022:
                        ratio = 414 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0040:
                        ratio = 363 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.005:
                        ratio = 322 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0065:
                        ratio = 313 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                     # Проверка выгодности для MAC-10 | Neon Rider (Factory New)
            if skin['Название'] == "MAC-10 | Neon Rider (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.0015:
                        ratio = 168 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0025:
                        ratio = 164 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0040:
                        ratio = 158 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.005:
                        ratio = 154 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0065:
                        ratio = 144 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.011:
                        ratio = 133 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0135:
                        ratio = 122 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0159:
                        ratio = 115 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                        # Проверка выгодности для USP-S | Printstream (Factory New)
            if skin['Название'] == "USP-S | Printstream (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.0015:
                        ratio = 1442 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.003:
                        ratio = 1395 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0045:
                        ratio = 1343 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.00599:
                        ratio = 1299 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.007:
                        ratio = 1250 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.009:
                        ratio = 1220 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    # Проверка выгодности для Glock-18 | Franklin (Factory New)
            if skin['Название'] == "Glock-18 | Franklin (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.001:
                        ratio = 505 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.002:
                        ratio = 452 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.003:
                        ratio = 430 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0040:
                        ratio = 404 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.005:
                        ratio = 390 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0075:
                        ratio = 370 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.01:
                        ratio = 344 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                             # Проверка выгодности для Desert Eagle | Printstream (Factory New)
            if skin['Название'] == "Desert Eagle | Printstream (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.0015:
                        ratio = 1116 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0025:
                        ratio = 1037 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0040:
                        ratio = 995 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.006:
                        ratio = 939 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0074:
                        ratio = 915 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.009:
                        ratio = 885 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.011:
                        ratio = 864 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.192, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0135:
                        ratio = 854 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.016:
                        ratio = 832 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.018:
                        ratio = 790 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.197, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
# Проверка выгодности для AWP | Wildfire (Factory New)
            if skin['Название'] == "AWP | Wildfire (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.011:
                        ratio = 1280 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.013:
                        ratio = 1255 / skin['Цена']
                        if ratio > 1.145:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.015:
                        ratio = 1236 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.017:
                        ratio = 1230 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.021:
                        ratio = 1192 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    # Проверка выгодности для StatTrak™ M4A1-S | Chantico's Fire (Factory New)
            if skin['Название'] == "StatTrak™ M4A1-S | Chantico's Fire (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.0033:
                        ratio = 3333 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.0043:
                        ratio = 2887 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.015:
                        ratio = 2250 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin) 
                    elif skin['Износ'] < 0.017:
                        ratio = 1180 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)    
                            # Проверка выгодности для M4A1-S | Control Panel (Factory New)
            if skin['Название'] == "M4A1-S | Control Panel (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.0021:
                        ratio = 358 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0032:
                        ratio = 332 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.004:
                        ratio = 325.5 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.006:
                        ratio = 308 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0088:
                        ratio = 295 / skin['Цена']
                        if ratio > 1.15:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                            # Проверка выгодности для P90 | Cold Blooded (Factory New)
            if skin['Название'] == "P90 | Cold Blooded (Factory New)":
                if skin['Износ'] is not None and skin['Цена'] is not None:
                    if skin['Износ'] < 0.002:
                        ratio = 480 / skin['Цена']
                        if ratio > 1.14:
                            print(f"  Этот скин выгодный! (Износ < 0.16, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0038:
                        ratio = 455 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.168, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0053:
                        ratio = 432 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.171, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.0066:
                        ratio = 415 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.175, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                    elif skin['Износ'] < 0.0088:
                        ratio = 399 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.18, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                    elif skin['Износ'] < 0.012:
                        ratio = 382 / skin['Цена']
                        if ratio > 1.16:
                            print(f"  Этот скин выгодный! (Износ < 0.187, ratio = {ratio:.2f})")
                            skin["ratio"] = ratio
                            выгода.append(skin)
                      
    except Exception as e:
        print(f"Ошибка при обработке {skin_name}: {e}")
    finally:
        if driver:
            driver.quit()


with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_url, skin, url) for skin, url in skin_to_url.items()]
    for future in futures:
        try:
            future.result()
        except Exception as e:
            print(f"Ошибка выполнения: {e}")

print("\nСписок всех выгодных скинов:")
for i, skin in enumerate(выгода, 1):
    print(f"Скин #{i}:")
    print(f"  Название: {skin['Название']}")
    print(f"  Износ: {skin['Износ']}")
    print(f"  Цена: {skin['Цена'] if skin['Цена'] is not None else 'Цена не найдена'}")
   
    if 'ratio' in skin:
        print(f"  Выгода : {skin['ratio']:.2f}")
    else:
        print("  Выгода (ratio): не рассчитана")
       
def run_script():
    try:
        result = subprocess.run(['python3', '1variant.py'], capture_output=True, text=True, timeout=300)
        return result.stdout if result.stdout else "Скрипт завершился без вывода."
    except subprocess.TimeoutExpired:
        return "Ошибка: скрипт выполнялся слишком долго и был остановлен."
    except Exception as e:
        return f"Ошибка при запуске скрипта: {e}"





