

# subscribe to event log for sushi pairs created
    # requires
    # - infura (probably not geth light)
    # - 

# parse the created pair ticker from the event

# submit the ticker prefixed with "$" to twitter API
    # https://developer.twitter.com/en/docs/twitter-api/metrics
    # https://developer.twitter.com/en/docs/twitter-api/tweets/counts/introduction


from web3 import Web3
import json
import asyncio
import time


INFURA_ENDPOINT = "https://mainnet.infura.io/v3/d2a360148a0140638d65675f3b922231"
w3 = Web3(Web3.HTTPProvider(INFURA_ENDPOINT))


SUSHI_FACTORY_V2 = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
SUSHI_FACTORY_ABI = json.loads(open("abi_sushi_v2.json").read())["result"]

USDT_CONTRACT = Web3.toChecksumAddress("0x26d0ee7d0fad46b0deb495fa09e283151438c102")
USDC_CONTRACT = Web3.toChecksumAddress("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
WETH_CONTRACT = Web3.toChecksumAddress("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

PAIR_BASE_CONTRACTS = [USDC_CONTRACT, USDT_CONTRACT, WETH_CONTRACT]

ERC20_ABI = json.loads(open("abi_erc20.json").read())["result"]

# erc20 = w3.eth.contract(address=TETHER_CONTRACT, abi=READ_SYMBOL_ABI)



def get_number_of_tweets(query):
    return 0

def main():
    sushi_contract = w3.eth.contract(address=SUSHI_FACTORY_V2, abi=SUSHI_FACTORY_ABI)
    pair_created_filter = sushi_contract.events.PairCreated.createFilter(fromBlock=13450360, toBlock='latest')
    events = pair_created_filter.get_all_entries()
    print("Example response content\n", events)

    while True:
        events = pair_created_filter.get_new_entries()
        print("events", events)
        if events:
            event = event[0]

            token_address = None
            if event[0]["args"]["token0"] not in PAIR_BASE_CONTRACTS:
                token_address = event[0]["args"]["token0"]
            else:
                token_address = event[0]["args"]["token1"]

            contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
            ticker = contract.functions.symbol().call()
            
            print("NEW TICKER IS", ticker)
            print("Scoring Twitter for energetic-memetic sentiment rating")
            
            # The number of tweets mentioning this ticker in the last 7 days
            num_tweets = get_number_of_tweets("$" + ticker)

            

        time.sleep(30)


if __name__ == '__main__':
    main()


