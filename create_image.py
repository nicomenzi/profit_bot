from PIL import Image, ImageDraw, ImageFont
from get_data import get_tx

async def generate_image(project_name, count_buy, count_sell, count_mint, avg_buy_price, avg_sell_price, profit, discord_id, potential_profit):
    with Image.open("background.png") as img:
        # Display project name, buy count, sell count, and profit in image
        d = ImageDraw.Draw(img)
        #fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 40)
        d.text((10,10), "Project Name: " + project_name,  fill=(0, 0, 0))
        d.text((10,30), "NFT Mint: " + str(count_mint),  fill=(0, 0, 0))
        d.text((10,50), "NFT Buy: " + str(count_buy),  fill=(0, 0, 0))
        d.text((10,70), "NFT Sell: " + str(count_sell),  fill=(0, 0, 0))
        d.text((10,90), "Still in wallet: " + str(count_buy + count_mint - count_sell),  fill=(0, 0, 0))
        d.text((10,110), "Profit: " + str(profit) + " ETH", fill=(0, 0, 0))
        d.text((10,130), "Average Buy Price: " + str(avg_buy_price) + " ETH", fill=(0, 0, 0))
        d.text((10,150), "Average Sell Price: " + str(avg_sell_price) + " ETH", fill=(0, 0, 0))
        d.text((10,170), "Potential Profit: " + str(potential_profit) + " ETH", fill=(0, 0, 0))
        img.save(f'pil_text_font{discord_id}.png')

def generate_image_time(count_buy, count_sell, profit, discord_id, timestamp):
    print("Timestamp:", timestamp)
