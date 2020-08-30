#bot.py

import os
import random
from dotenv import load_dotenv

#Google API
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#discord bot extention
import discord
from discord.ext import commands

scope=["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json",scope)

client = gspread.authorize(creds)

sheet = client.open("Eve Price List Discord").sheet1

#Discord code start
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
##TOKEN = 'NzQ3NDc1MDA1MjQzMzkyMDAw.X0PaWA.Fm3xmAXW6E0y9TLQD0CLF5E8_e0'

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='quote', help='Obtains quote for a selected ship')
async def price_list(prc, *, ship_name):

     ships = sheet.col_values(1)

     try:
         cell = sheet.find(ship_name)
         price_val = sheet.cell(cell.row, cell.col + 1).value 
         await prc.send('The ' + ship_name + ' is priced at ' + price_val + ' isk.') 
     except gspread.exceptions.CellNotFound:
         await prc.send(ship_name + ' is not found.') 
  
@price_list.error
async def price_list_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
       ships = sheet.col_values(1)
       await ctx.send(ships)
    
bot.run(TOKEN)
