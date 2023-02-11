import requests
from dotenv import load_dotenv
import os
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
    # Define the API key once and use it for all requests
    apikey = os.getenv("ETHERSCAN_KEY")
    nft_transactions_url = f"https://api.etherscan.io/api?module=account&action=tokennfttx&address={address}&sort=asc&apikey={apikey}"
    transactions_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=asc&apikey={apikey}"
    internal_transactions_url = f"https://api.etherscan.io/api?module=account&action=txlistinternal&address={address}&sort=asc&apikey={apikey}"

    # Make all the requests in one shot and store the results in variables
    response = requests.get(nft_transactions_url)
    nft_transactions = response.json()["result"]
    response = requests.get(transactions_url)
    transactions = response.json()["result"]
    response = requests.get(internal_transactions_url)
    internal_transactions = response.json()["result"]

    count_buy = 0
    count_sell = 0
    profit = 0
    gas_spent = 0
    project_name = ""

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
            count_buy += 1
        elif tx["from"].lower() == address.lower():
            count_sell += 1

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
                print("NFT Minted")

            else:
                value_in_eth = int(transaction[0]["value"]) / 10 ** 18
                print("Bought: " + tx["tokenName"] + " " + tx["tokenSymbol"] + " " + tx["tokenID"] + " for " + str(
                    value_in_eth) + " ETH")
                print(value_in_eth)
                profit -= value_in_eth
        elif tx["from"].lower() == address.lower():

            transaction = [d for d in internal_transactions if d['hash'] == tx['hash']]

            if not transaction:
                print("NFT Burned/Transferred")
            else:
                value_in_eth = int(transaction[0]["value"]) / 10 ** 18

                profit += value_in_eth


    return project_name, count_buy, count_sell, profit

