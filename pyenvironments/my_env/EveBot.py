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

sh = client.open("[SGP] EVE Master Discord")
sheet = sh.worksheet("Ore Reprocessing Tracker")
sheeta = sh.worksheet("Ore Reprocess Details")
sheetb = sh.worksheet("Materials Processed Locations")
sheetc = sh.worksheet("Bounty Tracker")

def next_available_row(sheet):
    str_list = list(filter(None, sheet.col_values(1)))
    return(str(len(str_list)+1))
    
#define ore list
import json

with open('initlist.json', 'r') as filehandle:
    ore_list = json.load(filehandle)

with open('loclist.json', 'r') as filehandle:
    loc_list = json.load(filehandle)
    
#Discord code start
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
##TOKEN = 'NzQ3NDc1MDA1MjQzMzkyMDAw.X0PaWA.Fm3xmAXW6E0y9TLQD0CLF5E8_e0'


bot = commands.Bot(command_prefix="ee!")
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='crt', help='Creates an order of ores to be reprocessed at a'\
             ' location. Execute using ee!crt <Ore Name> <Ore Amount>'\
             ' <Location>.')
async def ores_to_be_proced(ctx, ore_name, ore_amt, location):
    placed_by = str(ctx.author)
    next_row = next_available_row(sheet)

    if (ore_name in ore_list) and ore_amt.isnumeric() and (location in loc_list):
        last_order_id = sheet.cell(int(next_row) - 1,1).value

        sheet.update_cell(format(next_row), 1, int(last_order_id) + 1)

        sheet.update_cell(format(next_row), 2, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

        sheet.update_cell(format(next_row), 3, ore_name)

        sheet.update_cell(format(next_row), 4, ore_amt)

        sheet.update_cell(format(next_row), 5, str('0%'))

        sheet.update_cell(format(next_row), 6, location)

        sheet.update_cell(format(next_row), 7, placed_by) 

        sheet.update_cell(format(next_row), 18, 0)

        next_order_id = str(int(last_order_id) + 1)

        await ctx.send('Order number ID ' + next_order_id + ' created!' +
                   ' Reprocessors claim partial or full order using ee!clm' + 
                   ' <order id> <reprocessing amount>. ')
    else:
       print_ore_list = ' ;'.join(ore_list)
       print_loc_list = ' ;'.join(loc_list)
       await ctx.send('Incorrect ore name or ore amount or location. Please key one of' + 
                      ' the following: ' +
                      print_ore_list + ' ,a valid amount and one of these'\
                      ' locations: ' + print_loc_list)

@bot.command(name='clm', help='Claims a reprocessing order. Execute ee!clm'\
             ' <existing Order ID> <ore amount>. ')
async def reproc_accepted(ctx, order_id, reproc_amt):
    order_to_be_upd = int(order_id) + 2
    reprocessor = str(ctx.author)
    reproc_col = 8
    reproc_amt_col = 9
    stor_blk_col = 0
    order_tot = int(sheet.cell(order_to_be_upd, 4).value) 
    ore_clmed = int(sheet.cell(order_to_be_upd, 18).value) 
    upd_ore_clmed = int(reproc_amt) + ore_clmed
    
    if upd_ore_clmed > int(order_tot):
        await ctx.send('Your claim will exceed the total amount of Ores'\
                       ' for this order. Claim Rejected. Please try again.')
        return 
       
    if sheet.cell(order_to_be_upd, 1).value == "":
       await ctx.send('Invalid Order ID. Please check again.')
       return 

    for i in range(5):
        cur_reproc_col = (reproc_col + (i*2))
        cur_reprocessor = sheet.cell(order_to_be_upd, cur_reproc_col).value
        if reprocessor == cur_reprocessor:
           cur_ore_tot = sheet.cell(order_to_be_upd, cur_reproc_col + 1).value
           new_tot_ore = int(reproc_amt) + int(cur_ore_tot)
           ore_clmed += int(reproc_amt)
           sheet.update_cell(order_to_be_upd, cur_reproc_col + 1, new_tot_ore)
           sheet.update_cell(order_to_be_upd, 18, ore_clmed)
           await ctx.send('Existing reprocessor found. Your claim amount has'\
                          ' been added to a total of: ' + str(new_tot_ore)) 
           break

        elif cur_reprocessor == "":
            
           sheet.update_cell(order_to_be_upd, cur_reproc_col, reprocessor)
           sheet.update_cell(order_to_be_upd, cur_reproc_col + 1, 
                             int(reproc_amt))
           ore_clmed += int(reproc_amt)
           sheet.update_cell(order_to_be_upd, 18, ore_clmed)
           await ctx.send('Order has been claimed by ' + reprocessor +
                          ' succesfully!')
           break

        elif i == 4:
          await ctx.send('Only a maximum of 5 reprocessors allowed per Order ID.')

    perc_ore_clm = (ore_clmed/ order_tot) * 100
    wrt_ore_perc = str(perc_ore_clm) + '%'

    sheet.update_cell(order_to_be_upd, 5, wrt_ore_perc)
    await ctx.send(wrt_ore_perc + ' completed for Order ' + order_id +'.')                         

@ores_to_be_proced.error
async def proced_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You are missing a required input to place the order. '\
                       'Please enter ee!crt <Ore Name> <Ore Amount>'\
                       ' <Location>.')

@bot.command(name='rep', help ='Indicates ores processed by a reprocessor and'\
             ' outputs the materials generated based on reprocessing skill.'\
             ' Take note that this should only be executed based on your'\
             ' claimed orders. Execute using ee!rep <order id previously'\
             ' claimed> <processing efficiency percentage>') 
async def reproc_exec(ctx, order_id, proc_eff):
    order_to_check = int(order_id) + 2 
    exe_by = str(ctx.author) 
    reproc_col = 8
    reproc_amt_col = 9
    calc_eff = int(proc_eff) / 30 

    for i in range(5):
        cur_reproc_col = (reproc_col +(i*2))
        find_reproc = sheet.cell(order_to_check, cur_reproc_col).value             
        if exe_by == find_reproc:
            exe_by_ore = sheet.cell(order_to_check, 3).value
            exe_by_loc = sheet.cell(order_to_check, 6).value
            exe_by_amt = sheet.cell(order_to_check, cur_reproc_col + 1).value
            ore_cell = sheeta.find(exe_by_ore)
            ore_cell_row = ore_cell.row
            ore_cell_col = ore_cell.col
            loc_cell = sheetb.find(exe_by_loc)
            loc_cell_row = loc_cell.row
            loc_cell_col = loc_cell.col

            for j in range(8):
                mats_base = sheeta.cell(ore_cell_row, ore_cell_col + 3 + j).value
                reproc_mats = int(exe_by_amt) * calc_eff * int(mats_base)
                curr_mat = int(sheetb.cell(loc_cell_row, j + 2).value)
                curr_mat += reproc_mats
                sheetb.update_cell(loc_cell_row, j + 2, curr_mat)

            
            proc_val = sheetb.row_values(loc_cell_row)
            await ctx.send('Reprocess complete. Displaying processed material'\
                           ' amounts: ' )
            await ctx.send('Location: ' + proc_val[0])
            await ctx.send('Tritanium: ' + proc_val[1])
            await ctx.send('Pyerite: ' + proc_val[2])
            await ctx.send('Mexaillion: ' + proc_val[3])
            await ctx.send('Isogen: ' + proc_val[4])
            await ctx.send('Nocxium: ' + proc_val[5])   
            await ctx.send('Zydrine: ' + proc_val[6])
            await ctx.send('Megacyte: ' + proc_val[7])
            await ctx.send('Morphite: ' + proc_val[8])
            break    
        
        else:
            await ctx.send('You have not claimed this order. Please confirm'\
                           ' Order ID.') 
      
@bot.command(name='kill', help = 'Logs a kill for bounties. Issue ee!kill <ship'\
             ' type killed> <number of kills> to log your kills for bounty'\
             ' dispensation.')
async def bounty(ctx, ship_type, num_kill):
    next_row = next_available_row(sheetc)
    kill_by = str(ctx.author)
    ship_list = ['miner', 'frig', 'dessie', 'cruis', 'bats', 'nhauler', 'ehauler']

    try:
        kill_cell = sheetc.find(kill_by)
        kill_cell_row = kill_cell.row
        kill_cell_col = kill_cell.col
    except gspread.exceptions.CellNotFound:
        sheetc.update_cell(format(next_row), 1, kill_by)
        kill_cell = sheetc.find(kill_by)
        kill_cell_row = kill_cell.row
        kill_cell_col = kill_cell.col
        for i in range(7):
            sheetc.update_cell(kill_cell.row, kill_cell.col + 1 + i, 0)

    if ship_type in ship_list:
        if ship_type == 'frig':
           curr_kill = int(sheetc.cell(kill_cell.row, 2).value)
           ship_tbu = 2                
        elif ship_type == 'dessie':
           curr_kill = int(sheetc.cell(kill_cell.row, 3).value)
           ship_tbu = 3                
        elif ship_type == 'cruis': 
           curr_kill = int(sheetc.cell(kill_cell.row, 4).value)
           ship_tbu = 4                
        elif ship_type == 'bats':
           curr_kill = int(sheetc.cell(kill_cell.row, 5).value)
           ship_tbu = 5                
        elif ship_type == 'miner':
           curr_kill = int(sheetc.cell(kill_cell.row, 6).value)
           ship_tbu = 6
        elif ship_type == 'nhauler':
           curr_kill = int(sheetc.cell(kill_cell.row, 7).value)
           ship_tbu = 7
        elif ship_type == 'ehauler':
           curr_kill = int(sheetc.cell(kill_cell.row, 8).value)
           ship_tbu = 8
        curr_kill += int(num_kill)   
        sheetc.update_cell(kill_cell.row, ship_tbu, curr_kill)                    
        await ctx.send('Your kills have been logged!')
    else:
        await ctx.send('Please input one of the following; miner, frig, dessie,'\
                        ' cruis, bats, ehauler, nhauler as the ship type.')

@bot.command(name='payme', help = 'Issues an invoice for your bounty kills.')
async def bounty(ctx): 
    bnty_payto = str(ctx.author)
    bnty_cell = sheetc.find(bnty_payto)
    bnty_cell_col = bnty_cell.col
    bnty_cell_row = bnty_cell.row
    frig_isk=0
    dessie_isk=0
    cruis_isk=0
    bats_isk=0
    miner_isk=0
    nhauler_isk=0 
    ehauler_isk=0


    for i in range(7):
        kill_num = int(sheetc.cell(bnty_cell.row, i + 2).value)
        if i == 0:
           frig_isk = 100000 * kill_num
        elif i == 1:
           dessie_isk = 200000 * kill_num
        elif i == 2:
           cruis_isk = 500000 * kill_num
        elif i == 3:
           bats_isk = 0 * kill_num
        elif i == 4:
           if kill_num > 5: 
            miner_isk = 200000 * kill_num//5
        elif i == 5:
           nhauler_isk = 1000000 * kill_num
        elif i == 6:
           ehauler_isk = 5000000 * kill_num
      
 
    tot_bnty = frig_isk + dessie_isk + cruis_isk + bats_isk + miner_isk +\
    nhauler_isk + ehauler_isk   

    await ctx.send('You are currently owed ' + str(tot_bnty) + ' ISK in bounty!') 

@bot.command(name='resetkills', help = 'Resets the killboard after bounties are'\
             ' paid.')
async def reset(ctx):
    sheetc.resize(1)
    sheetc.resize(100)


bot.run(TOKEN)
