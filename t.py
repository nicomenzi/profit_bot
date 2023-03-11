import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from decimal import Decimal


def generate_image(project_name, count_buy, count_sell, count_mint, avg_buy_price, avg_sell_price, profit,
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
        d.text((1082, 1192), str(avg_buy_price)+ " Ξ",font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256), anchor="rb")
        d.text((1082, 1332), str(avg_sell_price) + " Ξ",font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256), anchor="rb")
        d.text((1082, 1516), str(count_buy + count_mint - count_sell),font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256), anchor="rb")
        d.text((1082, 1646), str(profit) + " Ξ",font=ImageFont.truetype(font_type, font_size_stats), fill=(256, 256, 256), anchor="rb")
        #
        d.text((1774, 1232), str(profit) + " Ξ",font=ImageFont.truetype(font_type, font_size_pnl), fill=(0, 225, 0), anchor="mb")
        d.text((1774, 1428),"(" + str(round(float(profit)*float(eth_price),2)) + "$)",font=ImageFont.truetype(font_type, font_size_pnl), fill=(0, 225, 0), anchor="mb")
        if avg_buy_price > 0:
            d.text((1774, 1624), str(Decimal(potential_profit / avg_buy_price * 100).to_integral()) + "%",font=ImageFont.truetype(font_type, font_size_pnl), fill=(0, 225, 0), anchor="mb")
        else:
             d.text((1774, 1624), " ∞ %",font=ImageFont.truetype(font_type, font_size_pnl), fill=(0, 225, 0),  anchor="mb")



        d.text((2022, 1998), user_name,font=ImageFont.truetype(font_type, 45), fill=(221, 174, 92), anchor="rb")
        d.text((2022, 1902), "@"+twitter_handle,font=ImageFont.truetype(font_type, 45), fill=(221, 174, 92), anchor="rb")


        #Get the image from the URL and resize it to 30 pixels
        response = requests.get(image_url)
        img_to_paste = Image.open(BytesIO(response.content)).resize((115, 115))

        # Paste the image onto the generated image
        img.paste(img_to_paste, (2060, 1818))



        img.save(f'pil_text_font{discord_id}.png')


#call
generate_image(project_name="CryptoPunks", count_buy=1, count_sell=0, count_mint=0, avg_buy_price=0.1, avg_sell_price=0.1, profit=0.1, potential_profit=0.1, image_url="https://storage.opensea.io/files/0d1b8b1b1b1b1b1b1b1b1b1b1b1b1b1b.svg", user_name="test", eth_price=1,discord_id=1, twitter_handle="test")