import disnake
from disnake.ext import commands
from disnake impor slash_commands

client = disnake.Client()

bot = commands.InteractionBot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.slash_command()
