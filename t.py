import requests
from dotenv import load_dotenv
import os
import calendar
import time
import asyncio
import aiohttp
from models import User, Wallet
load_dotenv()


def remove_duplicates(arr, attr):
    values = [i[attr] for i in arr]
    unique_values = set(values)

    result = []
    for value in unique_values:
        for i in arr:
            if i[attr] == value:
                result.append(i)
                break

    return result

def remove_duplicates_two(array1, array2, attr):
    values = set([i[attr] for i in array2])
    result = [i for i in array1 if i[attr] not in values]
    return result


async def make_request(session, url, headers=None, params=None):
    async with session.get(url, headers=headers, params=params) as response:
        return await response.json()


async def get_profit(address, contract_address):

    address = address.lower()
    contract_address = contract_address.lower()
    # Define variables
    count_buy = 0
    count_sell = 0
    count_mint = 0
    profit = 0
    gas_spent = 0
    sellprice = []
    buyprice = []
    minttx = []
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': os.getenv("TRANSPOSE_KEY"),
    }
    etherscan_api_key = os.getenv("ETHERSCAN_KEY")
    # -------------------------------------------------------------------------------------------------------------------
    # Prepare API calls
    # -------------------------------------------------------------------------------------------------------------------
    url_nft_tx = "https://api.transpose.io/nft/transfers-by-account"
    url_sales = "https://api.transpose.io/nft/sales-by-account"
    url_tx_etherscan = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=asc&apikey={etherscan_api_key}"

    params_get_nft_tx = {
        "chain_id": "ethereum",
        "account_address": address,
        "order": "desc",
        "limit" : "10000",
    }
    #-------------------------------------------------------------------------------------------------------------------
    # API calls and data cleaning
    #-------------------------------------------------------------------------------------------------------------------
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(make_request(session, url_nft_tx, headers=headers, params=params_get_nft_tx)),
            asyncio.create_task(make_request(session, url_sales, headers=headers, params=params_get_nft_tx)),
            asyncio.create_task(make_request(session, url_tx_etherscan))
        ]
        response_nft_tx, response_sales, response_tx_etherscan = await asyncio.gather(*tasks)

    nft_tx = response_nft_tx["results"]
    sales = response_sales["results"]
    tx_etherscan = response_tx_etherscan["result"]

    nft_tx_cleaned = remove_duplicates_two(nft_tx, sales, "transaction_hash")

    #-------------------------------------------------------------------------------------------------------------------

    for tx in sales:
        tx["contract_address"] = tx["contract_address"].lower()
        if tx["contract_address"] != contract_address:
            continue

        tx["buyer"] = tx["buyer"].lower()
        tx["seller"] = tx["seller"].lower()


        if tx["buyer"] == address:
            count_buy += 1
            buyprice.append(tx["eth_price"])
            profit -= tx["eth_price"]
            #calculate gas fees
            for tx_es in tx_etherscan:
                if tx["transaction_hash"] == tx_es["hash"]:
                    profit -= int(tx_es["gasPrice"]) * int(tx_es["gasUsed"]) / 10 ** 18
                    break
        elif tx["seller"] == address:
            count_sell += 1
            sellprice.append(tx["eth_price"]-tx["royalty_fee"]-tx["platform_fee"])
            profit += tx["eth_price"]-tx["royalty_fee"]-tx["platform_fee"]

    for tx in nft_tx_cleaned:
        tx["contract_address"] = tx["contract_address"].lower()
        if tx["contract_address"] != contract_address:
            continue
        if tx["category"] == "mint":
            count_mint += tx["quantity"]
            minttx.append(tx["transaction_hash"])
        if tx["category"] == "send" and tx["to_address"] == address:
            count_buy += 1
            buyprice.append(0)
        elif tx["category"] == "send" and tx["from_address"] == address:
            count_sell += 1
            sellprice.append(0)

    minttx = list(dict.fromkeys(minttx))

    #calculate gas fees
    for tx_es in tx_etherscan:
        for tx in minttx:
            if tx == tx_es["hash"]:
                profit -= int(tx_es["gasPrice"]) * int(tx_es["gasUsed"]) / 10 ** 18
                value = int(tx_es["value"]) / 10 ** 18
                buyprice.append(value)
                profit -= (int(tx_es["value"]) / 10 ** 18)
                break

    # calculate the payed gas fees for the transactions
    for tx in tx_etherscan:
        if tx["contractAddress"] != contract_address:
            continue

        if tx["to"].lower() == address:
            gas_in_eth = int(tx["gasPrice"]) * int(tx["gasUsed"]) / 10 ** 18
            profit -= gas_in_eth

    # calculate the payed gas fees for the token approval transactions
    for tx in tx_etherscan:
        if tx["to"].lower() == contract_address:
            if "0xa22cb465" == tx["methodId"]:
                gas_spent += int(tx["gasPrice"]) * int(tx["gasUsed"]) / 10 ** 18
                profit -= gas_spent

    return count_mint, count_buy, count_sell, buyprice, sellprice, profit

async def get_x_day_profit(address, block, timestamp):
    address = address.lower()

    # Define variables
    count_buy = 0
    count_sell = 0
    count_mint = 0
    profit = 0
    gas_spent = 0
    sellprice = []
    buyprice = []
    minttx = []
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': os.getenv("TRANSPOSE_KEY"),
    }
    etherscan_api_key = os.getenv("ETHERSCAN_KEY")

    url_nft_tx = "https://api.transpose.io/nft/transfers-by-account"
    url_sales = "https://api.transpose.io/nft/sales-by-account"
    url_tx_etherscan = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=asc&apikey={etherscan_api_key}&startblock={block}"

    params_get_nft_tx = {
        "chain_id": "ethereum",
        "account_address": address,
        "order": "desc",
        "limit" : "10000",
        "transferred_after": int(timestamp),
    }

    params_get_nft_sales = {
        "chain_id": "ethereum",
        "account_address": address,
        "order": "desc",
        "limit" : "10000",
        "sold_after": int(timestamp),
    }

    # -------------------------------------------------------------------------------------------------------------------
    # API calls and data cleaning
    # -------------------------------------------------------------------------------------------------------------------
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(make_request(session, url_nft_tx, headers=headers, params=params_get_nft_tx)),
            asyncio.create_task(make_request(session, url_sales, headers=headers, params=params_get_nft_sales)),
            asyncio.create_task(make_request(session, url_tx_etherscan))
        ]
        response_nft_tx, response_sales, response_tx_etherscan = await asyncio.gather(*tasks)

    nft_tx = response_nft_tx["results"]
    sales = response_sales["results"]
    tx_etherscan = response_tx_etherscan["result"]

    nft_tx_cleaned = remove_duplicates_two(nft_tx, sales, "transaction_hash")

    # -------------------------------------------------------------------------------------------------------------------
    # Calculate the profit
    # -------------------------------------------------------------------------------------------------------------------

    for tx in sales:
        tx["buyer"] = tx["buyer"].lower()
        tx["seller"] = tx["seller"].lower()

        if tx["buyer"] == address:
            count_buy += 1
            buyprice.append(tx["eth_price"])
            profit -= tx["eth_price"]
            #calculate gas fees
            for tx_es in tx_etherscan:
                if tx["transaction_hash"] == tx_es["hash"]:
                    profit -= int(tx_es["gasPrice"]) * int(tx_es["gasUsed"]) / 10 ** 18
                    break
        elif tx["seller"] == address:
            count_sell += 1
            sellprice.append(tx["eth_price"]-tx["royalty_fee"]-tx["platform_fee"])
            profit += tx["eth_price"]-tx["royalty_fee"]-tx["platform_fee"]

    for tx in nft_tx_cleaned:
        if tx["category"] == "mint":
            count_mint += tx["quantity"]
            minttx.append(tx["transaction_hash"])
            print(tx["transaction_hash"])
        #if tx["category"] == "send" and tx["to_address"] == address:
        #    count_buy += 1
        #    buyprice.append(0)
        #elif tx["category"] == "send" and tx["from_address"] == address:
        #    count_sell += 1
        #    sellprice.append(0)

    minttx = list(dict.fromkeys(minttx))

    #calculate gas fees
    for tx_es in tx_etherscan:
        for tx in minttx:
            if tx == tx_es["hash"]:
                profit -= int(tx_es["gasPrice"]) * int(tx_es["gasUsed"]) / 10 ** 18
                value = int(tx_es["value"]) / 10 ** 18
                buyprice.append(value)
                profit -= (int(tx_es["value"]) / 10 ** 18)
                break

    # calculate the payed gas fees for the transactions
    for tx in tx_etherscan:

        if tx["to"].lower() == address:
            gas_in_eth = int(tx["gasPrice"]) * int(tx["gasUsed"]) / 10 ** 18
            profit -= gas_in_eth

    # calculate the payed gas fees for the token approval transactions
    for tx in tx_etherscan:
        if "0xa22cb465" == tx["methodId"]:
            gas_spent += int(tx["gasPrice"]) * int(tx["gasUsed"]) / 10 ** 18
            profit -= gas_spent

    return count_mint, count_buy, count_sell, buyprice, sellprice, profit






async def get_collection_name(contract_address):
    url = "https://api.transpose.io/nft/collections-by-contract-address"
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': os.getenv("TRANSPOSE_KEY"),
    }
    params = {
        "chain_id": "ethereum",
        "contract_addresses": contract_address,
    }
    response = requests.get(url, headers=headers, params=params)
    return(response.json()["results"][0]["name"])

async def get_collection_floor_price(contract_address):
    url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{os.getenv('ALCHEMY_KEY')}/getFloorPrice?contractAddress={contract_address}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    fp = response.json()["openSea"]["floorPrice"]
    return fp

#call async functions
async def main():
    timestamp = int(time.time())
    print(timestamp)
    x_days_ago = timestamp - 30 * 24 * 60 * 60
    print(x_days_ago)

    get_block_url = f"https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={x_days_ago}&closest=before&apikey={os.getenv('ETHERSCAN_KEY')}"
    block = requests.get(get_block_url).json()["result"]
    count_mint, count_buy, count_sell, buyprice, sellprice, profit = await get_x_day_profit("0xfe59f409d7a05f8e24aa90626186cc820c8e3005", block, x_days_ago)
    print(count_mint, count_buy, count_sell, buyprice, sellprice, profit)


if __name__ == "__main__":
    asyncio.run(main())