import json
import disnake
from disnake.ext import commands
from selenium import webdriver
import time
import re
import shutil



intents = disnake.Intents.default()
intents.message_content = True  # Включаем интент message_content
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(
    name="search",
    description="Search for a name by price"
)
async def search(ctx, url: str, price: str):
    path = 'write-here-path-to-file/source-page.txt'
    data = {}
    Is_sayed = True
    Is_found = True
    try:
        while Is_found:
            driver = webdriver.Chrome()
            driver.maximize_window()
            driver.get(url=url)
            time.sleep(1)

            with open(path, 'w', encoding='utf-16') as fh:
                fh.write(driver.page_source)

            max_height = int(get_max_height(path))

            scroll_step = 500
            scrolls = max_height // scroll_step
            print(scrolls)

            for _ in range(scrolls+1):
                time.sleep(1)
                with open(path, 'w', encoding='utf-16') as fh:
                    driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                    fh.write(driver.page_source)
                    find_and_save_name_price(path, data)
                shutil.os.remove(path)

            save_to_json(data)
            names = find_names_by_price(price)
            if names:
                mention = ctx.author.mention
                await ctx.send(f"{mention}, найдены следующие имена с ценой {price}: {', '.join(names)}\nURL: {url}, Цена: {price}")
                break
            if Is_sayed:
                await ctx.send(f"Цена: {price}, я дам вам знать когда нужный лот будет найден")
                Is_sayed = False

    except Exception as _ex:
        print(_ex)

    finally:
        driver.quit()

def get_max_height(path):
    with open(path, 'r', encoding='utf-16') as fh:
        text = fh.read()
        pattern = r'<div\s+class="infinite-scroll"\s+style="[^"]*">'
        matches = re.findall(pattern, text)
        pattern = r'height:\s*(\d+)\s*px'
        height = re.findall(pattern, matches[0])
        return height[0]

def find_and_save_name_price(path, data):
    pattern = r'class="user__name--xF_ju">([^<]+).*?<b\s+class="price">(\d+)</b>'
    with open(path, 'r', encoding='utf-16') as fh:
        content = fh.read()
        matches = re.findall(pattern, content)
    for name, price in matches:
        data[name] = price 

def save_to_json(data):
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

def find_names_by_price(price):
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
        names = [name for name, p in data.items() if p == price]
        return names
    
bot.run('Your token')
#https://youtu.be/1N1iyaHJcm0
