import disnake
from disnake.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from create_image import generate_image, generate_image_time, generate_image_manual
from dotenv import load_dotenv
from models import User, Wallet, Base
from get_data_v2 import get_profit, get_collection_name, get_collection_floor_price, get_x_day_profit
import os
import time
import asyncio
import requests
load_dotenv()


#client = disnake.Client()

bot = commands.InteractionBot()

engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command()
async def profit(ctx, contract_address: str):
    #try:
        await ctx.response.defer()

        user_id = ctx.author.id
        user_avatar = ctx.author.display_avatar
        user_name = ctx.author.display_name


        count_buy = 0
        count_sell = 0
        count_mint = 0
        profit = 0
        sellprice = []
        buyprice = []


        # Get wallets for user from mysql database
        wallets = session.query(Wallet).filter_by(user_id=user_id).all()
        if len(wallets) == 0:
            await ctx.followup.send("You have no wallets added")
        else:
            # Get all transactions for all wallets
            for wallet in wallets:
                address = wallet.address
                count_mint_temp, count_buy_temp, count_sell_temp, buyprice_temp, sellprice_temp,  profit_temp = await get_profit(address, contract_address.lower())
                count_mint += count_mint_temp
                count_buy += count_buy_temp
                count_sell += count_sell_temp
                profit += profit_temp
                buyprice.extend(buyprice_temp)
                sellprice.extend(sellprice_temp)
            count = count_buy + count_mint
            print(buyprice)
            buy_price = sum(buyprice) / count
            print("e")
            print(sellprice)
            sell_price = sum(sellprice) / count_sell

            project_name = await get_collection_name(contract_address.lower())
            floor_price = await get_collection_floor_price(contract_address.lower())

            potential_profit = (floor_price * (count_buy + count_mint - count_sell)) + profit


            await generate_image(project_name, count_buy, count_sell, count_mint, buy_price, sell_price, profit, user_id, potential_profit, user_avatar, user_name)

            await ctx.followup.send(file=disnake.File(f'pil_text_font{user_id}.png'))
    #except Exception as e:
    #    print(e)
    #    await ctx.followup.send("Something went wrong")


@bot.slash_command()
async def add_wallet(ctx, address: str):
    await ctx.response.defer()
    # Add wallet to mysql database
    users = session.query(User).filter_by(user_id=ctx.author.id).all()
    if len(users) == 0:
        user = User(user_id=ctx.author.id, name=ctx.author.name)
        session.add(user)
        session.commit()

    wallet = Wallet(address=address.lower(), user_id=ctx.author.id)
    session.add(wallet)
    session.commit()

    await ctx.followup.send("Wallet added")

@bot.slash_command()
async def remove_wallet(ctx, address: str):
    await ctx.response.defer()
    # Remove wallet from mysql database
    users = session.query(User).filter_by(user_id=ctx.author.id).all()
    if len(users) == 0:
        await ctx.followup.send("You don't have any wallets")
    else:
        wallets = session.query(Wallet).filter_by(address=address.lower()).all()
        if len(wallets) == 0:
            await ctx.followup.send("Wallet not found")
        else:
            session.delete(wallets[0])
            session.commit()
            await ctx.followup.send("Wallet removed")

@bot.slash_command()
async def list_wallets(ctx):
    await ctx.response.defer(ephemeral=True)
    # List wallets from json file
    users = session.query(User).filter_by(user_id=ctx.author.id).all()
    if len(users) == 0:
        await ctx.followup.send("You don't have any wallets")
    else:
        wallets = session.query(Wallet).filter_by(user_id=ctx.author.id).all()
        if len(wallets) == 0:
            await ctx.followup.send("You don't have any wallets")
        else:
            wallet_list = ""
            for wallet in wallets:
                wallet_list += wallet.address + "\n"
            await ctx.followup.send(wallet_list, ephemeral=True)


@bot.slash_command()
async def profit_history(ctx, days: int):
    await ctx.response.defer()

    count_buy = 0
    count_sell = 0
    count_mint = 0
    profit = 0
    sellprice = []
    buyprice = []

    user_id = ctx.author.id

    # get 7d profit
    timestamp = int(time.time())
    x_days_ago = timestamp - days * 24 * 60 * 60

    get_block_url = f"https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={x_days_ago}&closest=before&apikey={os.getenv('ETHERSCAN_KEY')}"
    block = requests.get(get_block_url).json()["result"]


    users = session.query(User).filter_by(user_id=ctx.author.id).all()
    if len(users) == 0:
        await ctx.followup.send("You don't have any wallets")
    else:
        wallets = session.query(Wallet).filter_by(user_id=ctx.author.id).all()
        if len(wallets) == 0:
            await ctx.followup.send("You don't have any wallets")

        else:
            for wallet in wallets:
                address = wallet.address
                count_mint_temp, count_buy_temp, count_sell_temp, buyprice_temp, sellprice_temp,  profit_temp = await get_x_day_profit(address.lower(), block, x_days_ago)
                count_mint += count_mint_temp
                count_buy += count_buy_temp
                count_sell += count_sell_temp
                profit += profit_temp
                buyprice.extend(buyprice_temp)
                sellprice.extend(sellprice_temp)

            if count_buy == 0 and count_sell == 0 and count_mint == 0:
                await ctx.followup.send("No transactions found")
                return

            await generate_image_time(count_mint, count_buy, count_sell, profit, user_id, timestamp)
            await ctx.followup.send(file=disnake.File(f'profit_time{user_id}.png'))

@bot.slash_command()
async def manual_profit(ctx, type: str, amount: int, price_buy: float, price_sell: float):
    await ctx.response.defer()
    user_id = ctx.author.id
    await generate_image_manual(type, amount, price_buy, price_sell, user_id)
    await ctx.followup.send(file=disnake.File(f'manual{user_id}.png'))



@bot.slash_command()
async def help(ctx):
    await ctx.response.defer()
    await ctx.followup.send("Commands: \n"
                            "/add_wallet <address> - Add a wallet \n"
                            "/remove_wallet <address> - Remove a wallet\n"
                            "/list_wallets - List all your wallets\n"
                            "/profit_history <days> - Get profit history for the last x days \n"
                            "/manual_profit <type> <amount> <price_buy> <price_sell> - Get profit for a profit of any kind\n"
                            "/profit - Get profit for all of your wallets from a certain collection \n"
                            "/help - Show help \n")



if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))



