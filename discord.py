import disnake
from disnake.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from create_image import generate_image
from dotenv import load_dotenv
from models import User, Wallet, Base
import os
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
async def profit(ctx, address: str, contract_address: str):
    await ctx.response.defer()

    user_id = ctx.author.id


    generate_image(address.lower(), contract_address.lower(), user_id)

    await ctx.followup.send(file=disnake.File(f'pil_text_font{user_id}.png'))


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
async def sevendayprofit(ctx, address: str):
    await ctx.response.defer()
    # get 7d profit

    await ctx.followup.send("7d profit listed")

@bot.slash_command()
async def fifteendayprofit(ctx, address: str):
    await ctx.response.defer()
    # get 15d profit

    await ctx.followup.send("15d profit listed")

@bot.slash_command()
async def thirtydayprofit(ctx, address: str):
    await ctx.response.defer()
    # get 30d profit

    await ctx.followup.send("30d profit listed")





bot.run(os.getenv("DISCORD_TOKEN"))


