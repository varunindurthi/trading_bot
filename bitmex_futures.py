import requests
import pprint

def get_contracts(): 
    response_object = requests.get("https://testnet.bitmex.com/api/v1/instrument/active")
    contracts = [] 
    for entry in response_object.json():
        symbol = entry['symbol']
        contracts.append(symbol)
    return contracts

    
    # return contracts
print(get_contracts())