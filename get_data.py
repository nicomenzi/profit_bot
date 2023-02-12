import requests
from dotenv import load_dotenv
import os
import calendar
import time
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

def get_tx(address, contract_address):
    # Get wallets for user from mysql database



    # Define the API key once and use it for all requests
    apikey = os.getenv("ETHERSCAN_KEY")
    nft_transactions_url = f"https://api.etherscan.io/api?module=account&action=tokennfttx&address={address}&sort=asc&apikey={apikey}"
    erc1155_transactions_url = f"https://api.etherscan.io/api?module=account&action=token1155tx&address={address}&sort=asc&apikey={apikey}"
    transactions_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=asc&apikey={apikey}"
    internal_transactions_url = f"https://api.etherscan.io/api?module=account&action=txlistinternal&address={address}&sort=asc&apikey={apikey}"

    # Make all the requests in one shot and store the results in variables
    response_erc721_tx = requests.get(nft_transactions_url)
    response_erc1155_tx = requests.get(erc1155_transactions_url)
    response_tx = requests.get(transactions_url)
    response_internal_tx = requests.get(internal_transactions_url)


    # Extract the JSON data from the response
    nft_transactions = response_erc721_tx.json()["result"]
    erc1155_transactions = response_erc1155_tx.json()["result"]
    transactions = response_tx.json()["result"]
    internal_transactions = response_internal_tx.json()["result"]



    # Merge erc 721 and erc 1155 transactions
    nft_transactions.extend(erc1155_transactions)
    #print(nft_transactions)






    count_mint = 0
    count_buy = 0
    count_sell = 0
    profit = 0
    gas_spent = 0
    project_name = ""
    buy_price = []
    sell_price = []

    # calculate the payed gas fees for the token approval transactions
    for tx in transactions:
        if tx["to"] == contract_address:
            if "0xa22cb465" == tx["methodId"]:
                gas_spent += int(tx["gasPrice"]) * int(tx["gasUsed"]) / 10 ** 18
                profit -= gas_spent


    for tx in nft_transactions:
        # Skip transactions that don't match the contract address
        if tx["contractAddress"] != contract_address:
            continue

        # Determine if the transaction is a receive or transfer event
        if tx["to"].lower() == address.lower():
            for i in transactions:
                if i["hash"] == tx["hash"] and (i["methodId"] == "0xa0712d68" or i["methodId"] == "0x26c858a4"):
                    count_mint += 1
                elif i["hash"] == tx["hash"]:
                    count_buy += 1
        elif tx["from"].lower() == address.lower():
            count_sell += 1

    print("Minted: " + str(count_mint))
    print("Bought: " + str(count_buy))
    print("Sold: " + str(count_sell))
    # clean up transactions
    nft_transactions = remove_duplicates(nft_transactions, "hash")

    # calculate the payed gas fees for the transactions
    for tx in nft_transactions:
        if tx["contractAddress"] != contract_address:
            continue

        if tx["to"].lower() == address.lower():
            gas_in_eth = int(tx["gasPrice"]) * int(tx["gasUsed"]) / 10 ** 18
            profit -= gas_in_eth


    for tx in nft_transactions:
        result = []
        # Skip transactions that don't match the contract address
        if tx["contractAddress"] != contract_address:
            continue

        if project_name == "":
            project_name = tx["tokenName"]

        # Determine if the transaction is a receive or transfer event
        if tx["to"].lower() == address.lower():

            transaction = [d for d in transactions if d['hash'] == tx['hash']]
            if not transaction:
                print("NFT Received")

            else:
                value_in_eth = int(transaction[0]["value"]) / 10 ** 18
                print("Bought: " + tx["tokenName"] + " " + tx["tokenSymbol"] + " " + tx["tokenID"] + " for " + str(
                    value_in_eth) + " ETH")
                print(value_in_eth)
                buy_price.append(value_in_eth)
                profit -= value_in_eth
        elif tx["from"].lower() == address.lower():

            transaction = [d for d in internal_transactions if d['hash'] == tx['hash']]

            if not transaction:
                print("NFT Burned/Transferred")
            else:
                value_in_eth = int(transaction[0]["value"]) / 10 ** 18
                sell_price.append(value_in_eth)
                profit += value_in_eth

    #get average buy price and sell price
    print(buy_price)
    print(sell_price)
    if len(buy_price) > 0:
        buy_price = sum(buy_price) / (count_buy + count_mint)
    if len(sell_price) > 0:
        sell_price = sum(sell_price) / count_sell

    print(buy_price)
    print(sell_price)


    return project_name, count_buy, count_sell, count_mint, profit


def get_time_profit(address, timestamp):
    # Define the API key once and use it for all requests
    apikey = os.getenv("ETHERSCAN_KEY")
    #get block number for timestamp
    block_number_url = f"https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={apikey}"
    response_block_number = requests.get(block_number_url)
    block_number = response_block_number.json()["result"]

    #get transactions for block number
    nft_transactions_url = f"https://api.etherscan.io/api?module=account&action=tokennfttx&address={address}&startblock={block_number}&sort=asc&apikey={apikey}"
    erc1155_transactions_url = f"https://api.etherscan.io/api?module=account&action=token1155tx&address={address}&startblock={block_number}&sort=asc&apikey={apikey}"
    transactions_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock={block_number}&sort=asc&apikey={apikey}"
    internal_transactions_url = f"https://api.etherscan.io/api?module=account&action=txlistinternal&address={address}&startblock={block_number}&sort=asc&apikey={apikey}"

    # Make all the requests in one shot and store the results in variables
    response_erc721_tx = requests.get(nft_transactions_url)
    response_erc1155_tx = requests.get(erc1155_transactions_url)
    response_tx = requests.get(transactions_url)
    response_internal_tx = requests.get(internal_transactions_url)

    count_buy = 0
    count_sell = 0
    profit = 0
    gas_spent = 0

    nft_transactions = response_erc721_tx.json()["result"]
    erc1155_transactions = response_erc1155_tx.json()["result"]
    transactions = response_tx.json()["result"]
    internal_transactions = response_internal_tx.json()["result"]

    # Merge erc 721 and erc 1155 transactions
    nft_transactions.extend(erc1155_transactions)

    # clean up transactions
    nft_transactions = remove_duplicates(nft_transactions, "hash")
    traded_contracts = remove_duplicates(nft_transactions, "contractAddress")

    # calculate the payed gas fees for the token approval transactions








    print("Timestamp:", timestamp)

