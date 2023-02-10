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

bot.run(os.getenv("DISCORD_TOKEN"))


