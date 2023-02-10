from PIL import Image, ImageDraw, ImageFont
from get_data import get_tx

def generate_image(address, contract_address, discord_id):

    project_name, count_buy, count_sell, profit = get_tx(address, contract_address)


    # Display project name, buy count, sell count, and profit in image
    img = Image.open("background.png")
    d = ImageDraw.Draw(img)
    #fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 40)
    d.text((10,10), "Project Name" + project_name,  fill=(0, 0, 0))
    d.text((10,30), "NFT Buy: " + str(count_buy),  fill=(0, 0, 0))
    d.text((10,50), "NFT Sell: " + str(count_sell),  fill=(0, 0, 0))
    d.text((10,70), "Still in wallet: " + str(count_buy - count_sell),  fill=(0, 0, 0))
    d.text((10,90), "Profit: " + str(profit) + " ETH", fill=(0, 0, 0))
    img.save(f'pil_text_font{discord_id}.png')
