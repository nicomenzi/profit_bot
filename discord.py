import disnake
from disnake.ext import commands
from create_image import generate_image
from dotenv import load_dotenv
import os
load_dotenv()

client = disnake.Client()

bot = commands.InteractionBot()

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
    # Add wallet to json file


    await ctx.followup.send("Wallet added")

@bot.slash_command()
async def remove_wallet(ctx, address: str):
    await ctx.response.defer()
    # Remove wallet from json file


    await ctx.followup.send("Wallet removed")

@bot.slash_command()
async def list_wallets(ctx):
    await ctx.response.defer()
    # List wallets from json file

    await ctx.followup.send("Wallets listed")

@bot.slash_command()
async def SevenDayProfit(ctx, address: str):
    await ctx.response.defer()
    # get 7d profit

    await ctx.followup.send("7d profit listed")

@bot.slash_command()
async def FifteenDayProfit(ctx, address: str):
    await ctx.response.defer()
    # get 15d profit

    await ctx.followup.send("15d profit listed")

@bot.slash_command()
async def ThirtyDayProfit(ctx, address: str):
    await ctx.response.defer()
    # get 30d profit

    await ctx.followup.send("30d profit listed")





bot.run(os.getenv("DISCORD_TOKEN"))


