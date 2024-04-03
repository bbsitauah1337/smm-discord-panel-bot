import discord
from discord.ext import commands
import requests
import json
import os
from datetime import datetime
from config import DISCORD_TOKEN, API_URL
from colorama import Fore

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

API_URL = API_URL

DISCORD_TOKEN = DISCORD_TOKEN

@bot.event
async def on_ready():
    for _ in range(1000):
        await bot.wait_until_ready()
        print("This code is leaked in https://github.com/bbsitauah1337/smm-discord-panel-bot and credits to sociality.lol")
    
    os.system('cls' if os.name == 'nt' else 'clear')
    await bot.change_presence(activity=discord.Game(name="sociality.lol", type=3))

    print(f'Conectado como {bot.user.name}')

    print("Credits for https://github.com/bbsitauah1337/smm-discord-panel-bot and sociality.lol")

    print("Available Commands:")
    for command in bot.commands:
        print(f"{Fore.GREEN} [{Fore.WHITE} + {Fore.GREEN}]{Fore.RESET}!{command.name}")

DATA_FILE = 'data.json'

KEYS_FILE = 'keys.json'

def load_user_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(user_data):
    with open(DATA_FILE, 'w') as file:
        json.dump(user_data, file)

def load_keys():
    try:
        with open(KEYS_FILE, 'r') as file:
            keys_data = json.load(file)
            return keys_data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_key(user_id, key):
    keys = load_keys()
    keys[user_id] = {'key': key, 'registration_time': str(datetime.now())}
    with open(KEYS_FILE, 'w') as file:
        json.dump(keys, file)

@bot.command()
async def register_key(ctx, key):
    save_key(str(ctx.author.id), key)
    await ctx.send("Key registration successful!")

@bot.command()
async def info(ctx):
    user_id = str(ctx.author.id)
    keys = load_keys()
    user_data = keys.get(user_id)

    if user_data:
        key = user_data['key']
        registration_time = user_data['registration_time']
    else:
        registration_time = "Not registered"

    embed = discord.Embed(
        title="User Information",
        description=f"User: {ctx.author.name}\nUser ID: {user_id}\nRegistration Time: {registration_time}\nKey: ||xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx||",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

    if user_data:
        dm_embed = discord.Embed(
            title="Your Registration Information",
            description=f"User ID: {user_id}\nRegistration Time: {registration_time}\nKey: ||{key}||",
            color=discord.Color.blue()
        )
        await ctx.author.send(embed=dm_embed)

@bot.command()
async def add_order(ctx, service_id, link, quantity):
    user_id = str(ctx.author.id)
    keys = load_keys()
    if user_id not in keys:
        await ctx.send("You need to register your key first using !register_key <key>")
        return
    key = keys[user_id]

    payload = {
        'key': key,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }

    response = requests.post(API_URL, data=payload)

    if response.status_code == 200:
        data = response.json()
        order_id = data.get('order')

        status_payload = {
            'key': key,
            'action': 'status',
            'order': order_id
        }
        status_response = requests.post(API_URL, data=status_payload)
        if status_response.status_code == 200:
            status_data = status_response.json()
            charge = status_data.get('charge')
            currency = status_data.get('currency')
        else:
            charge = "N/A"
            currency = "N/A"

        user_profile = {
            'username': ctx.author.name,
            'user_id': str(ctx.author.id),
            'link': link,
            'price': charge,
            'currency': currency,
            'quantity': quantity
        }

        user_data = load_user_data()

        user_data[order_id] = user_profile

        save_user_data(user_data)

        await ctx.send(f"Order successfully placed! Order ID: {order_id}")

    else:
        await ctx.send("Failed to add order. Please try again later.")

@bot.command()
async def stats(ctx):
    user_data = load_user_data()

    canceled = 0
    delivered = 0
    in_progress = 0
    order_ids = []

    for order_id, profile in user_data.items():
        order_ids.append(order_id)
        if int(order_id) % 2 == 0:
            delivered += 1
        else:
            in_progress += 1

    total_orders = canceled + delivered + in_progress

    stats_message = f"Total Orders: {total_orders}\n"
    stats_message += f"Canceled Orders: {canceled}\n"
    stats_message += f"Delivered Orders: {delivered}\n"
    stats_message += f"In Progress Orders: {in_progress}\n"
    stats_message += f"Order IDs: {', '.join(map(str, order_ids))}"

    await ctx.send(stats_message)

@bot.command()
async def order_info(ctx, order_id: int):
    user_data = load_user_data()

    if str(order_id) not in user_data:
        await ctx.send("The order ID does not exist.")
        return

    order_info = user_data[str(order_id)]
    username = order_info['username']
    user_id = order_info['user_id']
    link = order_info['link']
    price = order_info['price']
    currency = order_info['currency']
    quantity = order_info['quantity']

    user_id = str(ctx.author.id)
    keys = load_keys()
    if user_id not in keys:
        await ctx.send("You need to register your key first using !register_key <key>")
        return
    key = keys[user_id]

    status_payload = {
        'key': key,
        'action': 'status',
        'order': order_id
    }
    status_response = requests.post(API_URL, data=status_payload)

    if status_response.status_code == 200:
        status_data = status_response.json()
        status = status_data.get('status')
    else:
        status = "Unknown"

    if status == "Canceled":
        embed_color = discord.Color.red()
    elif status == "Pending":
        embed_color = discord.Color.gold()
    elif status == "Completed":

        embed_color = discord.Color.green()
    else:
        embed_color = discord.Color.blue()

    embed = discord.Embed(
        title=f"Order ID: {order_id}",
        color=embed_color
    )
    embed.add_field(name="Username", value=username, inline=False)
    embed.add_field(name="User ID", value=user_id, inline=False)
    embed.add_field(name="Link", value=link, inline=False)
    embed.add_field(name="Price", value=f"{price} {currency}", inline=False)
    embed.add_field(name="Quantity", value=quantity, inline=False)
    embed.add_field(name="Status", value=status, inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def help_commands(ctx):
    embed = discord.Embed(
        title="Available Commands",
        description="List of all available commands:",
        color=discord.Color.green()
    )
    for command in bot.commands:
        embed.add_field(name=command.name, value=command.help, inline=False)
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)
