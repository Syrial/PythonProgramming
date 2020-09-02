#EveBot.py

import os
import random
import datetime
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

sheet = client.open("[SGP] EVE Master Discord").sheet1

def next_available_row(sheet):
    str_list = list(filter(None, sheet.col_values(1)))
    return(str(len(str_list)+1))
    
#Discord code start
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
##TOKEN = 'NzQ3NDc1MDA1MjQzMzkyMDAw.X0PaWA.Fm3xmAXW6E0y9TLQD0CLF5E8_e0'


bot = commands.Bot(command_prefix="ee!")
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='reproc', help='Determine and track the reprocessing status of materials. Execute using ee!reproc <Ore Name> <Ore Amount>')
async def ores_to_be_proced(ctx, ore_name, ore_amt):
    next_row = next_available_row(sheet)

    last_order_id = sheet.cell(int(next_row) - 1,1).value

    sheet.update_cell(format(next_row), 1, int(last_order_id) + 1)

    sheet.update_cell(format(next_row), 2, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    sheet.update_cell(format(next_row), 3, ore_name)

    sheet.update_cell(format(next_row), 4, ore_amt)

    sheet.update_cell(format(next_row), 5, str('0%'))

    next_order_id = str(int(last_order_id) + 1)

    await ctx.send('Order number ID ' + next_order_id + ' created!' +
                   ' Reprocessors execute order using ee!proc <order id> <reprocessing amount> for booking''')

@bot.command(name='proc', help='Accepts reprocessing order.')
async def reproc_accepted(ctx, order_id, reproc_amt):
    order_to_be_upd = int(order_id) + 2
    reprocessor = str(ctx.author)

    sheet.update_cell(format(order_to_be_upd), 6, reprocessor) 
    
    sheet.update_cell(format(order_to_be_upd), 7, int(reproc_amt))

    full_amnt = sheet.cell(order_to_be_upd, 4).value
    percent_done = str(int(reproc_amt)/int(full_amnt) * 100) + '%'

    sheet.update_cell(format(order_to_be_upd), 5, percent_done)
    await ctx.send('Order number ID ' + order_id + ' claimed by ' +\
                   reprocessor + '. Order has been ' + percent_done + ' fulfilled.')

   
bot.run(TOKEN)
