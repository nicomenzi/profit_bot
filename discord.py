import disnake
from disnake.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from create_image import generate_image, generate_image_time
from dotenv import load_dotenv
from models import User, Wallet, Base
from get_data_v2 import get_profit, get_collection_name, get_collection_floor_price
import os
import time
import asyncio
load_dotenv()


client = disnake.Client()

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


            await generate_image(project_name, count_buy, count_sell, count_mint, buy_price, sell_price, profit, user_id)

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
async def profit_history(ctx, address: str, days: int):
    await ctx.response.defer()

    count_buy = 0
    count_sell = 0
    profit = 0

    user_id = ctx.author.id

    # get 7d profit
    timestamp = int(time.time())
    x_days_ago = timestamp - days * 24 * 60 * 60

    users = session.query(User).filter_by(user_id=ctx.author.id).all()
    if len(users) == 0:
        await ctx.followup.send("You don't have any wallets")
    else:
        wallets = session.query(Wallet).filter_by(address=address.lower()).all()
        if len(wallets) == 0:
            await ctx.followup.send("You don't have any wallets")

        else:
            for wallet in wallets:
                address = wallet.address
                count_buy_temp, count_sell_temp, profit_temp = get_time_profit(address, x_days_ago)
                count_buy += count_buy_temp
                count_sell += count_sell_temp
                profit += profit_temp

            generate_image_time(count_buy, count_sell, profit, user_id, x_days_ago)



    await ctx.followup.send("7d profit listed")

@bot.slash_command()
async def fifteendayprofit(ctx, address: str):
    await ctx.response.defer()
    # get 15d profit
    timestamp = int(time.time())
    seven_days_ago = timestamp - 15 * 24 * 60 * 60

    await ctx.followup.send("15d profit listed")

@bot.slash_command()
async def thirtydayprofit(ctx, address: str):
    await ctx.response.defer()
    # get 30d profit
    timestamp = int(time.time())
    seven_days_ago = timestamp - 30 * 24 * 60 * 60

    await ctx.followup.send("30d profit listed")



async def main():
    loop = asyncio.get_running_loop()
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())


#if __name__ == "__main__":
#    loop = asyncio.get_event_loop()
#    loop.create_task(client.start(os.getenv('DISCORD_TOKEN')))
#    #loop.create_task(bot.start(os.getenv('DISCORD_TOKEN')))
#    loop.run_forever()



