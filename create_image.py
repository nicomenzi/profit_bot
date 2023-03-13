import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from decimal import Decimal

async def center_text_title(d: ImageDraw, text: str, x: int, y: int) -> tuple:
    font_size = 35
    font_type = "OpenSans-Bold.ttf"
    font = ImageFont.truetype(font_type, font_size)
    text_width, text_height = d.textsize(text, font=font)
    x_start = x - text_width // 2
    y_start = y - text_height // 2
    return x_start, y_start

async def center_text_stats(d: ImageDraw, text: str, x: int, y: int) -> tuple:
    font_size = 32
    font_type = "OpenSans-Bold.ttf"
    font = ImageFont.truetype(font_type, font_size)
    text_width, text_height = d.textsize(text, font=font)
    x_start = x - text_width // 2
    y_start = y - text_height // 2
    return x_start, y_start

async def center_text_pnl(d: ImageDraw, text: str, x: int, y: int) -> tuple:
    font_size = 45
    font_type = "OpenSans-Bold.ttf"
    font = ImageFont.truetype(font_type, font_size)
    text_width, text_height = d.textsize(text, font=font)
    x_start = x - text_width // 2
    y_start = y - text_height // 2
    return x_start, y_start




async def generate_image(project_name, count_buy, count_sell, count_mint, avg_buy_price, avg_sell_price, profit,
                          potential_profit, image_url, user_name, eth_price,discord_id, twitter_handle ):
    with Image.open("background_new.png") as img:


        avg_buy_price = round(avg_buy_price, 2)
        avg_sell_price = round(avg_sell_price, 2)
        profit = round(profit, 2)
        potential_profit = round(potential_profit, 2)



        # Display project name, buy count, sell count, and profit in image
        d = ImageDraw.Draw(img)
        font_size =96
        font_size_pnl = 80
        font_size_stats = 60
        font_type = "./PressStart2P-Regular.ttf"


        # fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 40)

        d.text((1200, 568), project_name, font=ImageFont.truetype(font_type, font_size), fill=(206, 122, 38), anchor="mm")
        d.text((1082, 926),str(count_buy),font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256), anchor="rb")
        d.text((1082, 1058), str(count_mint),font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256),anchor="rb")
        d.text((1082, 1192), str(avg_buy_price)+ "Ξ",font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256), anchor="rb")
        d.text((1082, 1332), str(avg_sell_price) + "Ξ",font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256), anchor="rb")
        d.text((1082, 1516), str(count_buy + count_mint - count_sell),font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256), anchor="rb")
        d.text((1082, 1646), str(profit) + "Ξ",font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256), anchor="rb")
        #
        d.text((1774, 1232), str(profit) + "Ξ",font=ImageFont.truetype(font_type, font_size_pnl), fill=(0, 225, 0), anchor="mb")
        d.text((1774, 1428),"" + str(round(float(profit)*float(eth_price),2)) + "$",font=ImageFont.truetype(font_type, font_size_pnl), fill=(0, 225, 0), anchor="mb")
        if avg_buy_price > 0:
            d.text((1774, 1624), str(Decimal(potential_profit / avg_buy_price * 100).to_integral()) + "%",font=ImageFont.truetype(font_type, font_size_pnl), fill=(0, 225, 0), anchor="mb")
        else:
             d.text((1774, 1624), " ∞ %",font=ImageFont.truetype(font_type, font_size_pnl), fill=(0, 225, 0),  anchor="mb")



        d.text((2022, 1998), user_name,font=ImageFont.truetype(font_type, 45), fill=(221, 174, 92), anchor="rb")
        d.text((2022, 1902), "@"+twitter_handle,font=ImageFont.truetype(font_type, 45), fill=(221, 174, 92), anchor="rb")


        #Get the image from the URL and resize it to 30 pixels
        response = requests.get(image_url)
        img_to_paste = Image.open(BytesIO(response.content)).resize((230, 230))

        # Paste the image onto the generated image
        img.paste(img_to_paste, (2060, 1818))



        img.save(f'pil_text_font{discord_id}.png')


async def generate_image_time(count_mint, count_buy, count_sell, profit, discord_id, timestamp):
    with Image.open("background.png") as img:
        d = ImageDraw.Draw(img)
        #fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 40)
        d.text((10,30), "NFT Mint: " + str(count_mint),  fill=(0, 0, 0))
        d.text((10,50), "NFT Buy: " + str(count_buy),  fill=(0, 0, 0))
        d.text((10,70), "NFT Sell: " + str(count_sell),  fill=(0, 0, 0))
        d.text((10,90), "Still in wallet: " + str(count_buy + count_mint - count_sell),  fill=(0, 0, 0))
        d.text((10,110), "Profit: " + str(profit) + " ETH", fill=(0, 0, 0))
        img.save(f'profit_time{discord_id}.png')


async def generate_image_manual(type, amount, price_buy,price_sell, user_id, user_name, image_url):
    with Image.open("background.png") as img:
        d = ImageDraw.Draw(img)
        #fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 40)
        d.text((10,10), "Type: " + type,  fill=(0, 0, 0))
        d.text((10,30), "Amount: " + str(amount),  fill=(0, 0, 0))
        d.text((10,50), "Price Buy: " + str(price_buy),  fill=(0, 0, 0))
        d.text((10,70), "Price Sell: " + str(price_sell),  fill=(0, 0, 0))
        d.text((10,90), "User: " + user_name,  fill=(0, 0, 0))

        # Get the image from the URL and resize it to 30 pixels
        response = requests.get(image_url)
        img_to_paste = Image.open(BytesIO(response.content)).resize((30, 30))

        img.save(f'manual{user_id}.png')


async def generate_image_PNL(token, type, exchange, ROI, entry, exit,  user_id, user_avatar, user_name):
    with Image.open("background.png") as img:
        d = ImageDraw.Draw(img)
        #fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 40)
        d.text((10,10), "Token: " + token,  fill=(0, 0, 0))
        d.text((10,30), "Type: " + type,  fill=(0, 0, 0))
        d.text((10,50), "Exchange: " + exchange,  fill=(0, 0, 0))
        d.text((10,70), "ROI: " + str(ROI),  fill=(0, 0, 0))
        d.text((10,90), "Entry: " + str(entry),  fill=(0, 0, 0))
        d.text((10,110), "Exit: " + str(exit),  fill=(0, 0, 0))
        d.text((10,130), "User: " + user_name,  fill=(0, 0, 0))

        # Get the image from the URL and resize it to 30 pixels
        response = requests.get(user_avatar)
        img_to_paste = Image.open(BytesIO(response.content)).resize((30, 30))

        img.save(f'PNL{user_id}.png')



