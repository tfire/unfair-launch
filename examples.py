from private import infura_api

import utils
import time
import json
import asyncio
import websockets

def poll_http_provider_example():
    sushi_contract = utils.w3.eth.contract(address=utils.SUSHI_FACTORY_V2, abi=utils.SUSHI_FACTORY_ABI)
    pair_created_filter = sushi_contract.events.PairCreated.createFilter(fromBlock="latest")

    print("\n\n")
    while True:
        events = pair_created_filter.get_new_entries()
        print("events", events)
        for event in events:
            token_address = utils.get_main_token_for_pair(event["args"]["token0"], event["args"]["token1"])
            ticker = utils.get_ticker_at_erc20(token_address)

            print("Scoring Twitter for energetic-memetic sentiment rating on cashtag $" + ticker)
            # The tweets mentioning this cashtag ticker in the last 7 days
            tweets, stats = utils.get_tweets("$" + ticker)
            print(stats)

        time.sleep(30)

async def listen_for_ws_events_example():
    async with websockets.connect(infura_api.INFURA_WS) as ws:
        await ws.send(json.dumps(
            {
                "id": 1, "method": "eth_subscribe", "params": ["logs", {
                    "address": [utils.SUSHI_FACTORY_V2],
                    "topics": [utils.w3.keccak(text="PairCreated(address,address,address,uint256)").hex()]
                }]
            }
        ))
        subscription_response = await ws.recv()
        print(subscription_response)

        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=60)
                print("message", message)
                decoded = utils.decode_PairCreated(message)
                print(decoded)
            except Exception as exc:
                print(exc)

def event_output_example():
    sushi_contract = utils.w3.eth.contract(address=utils.SUSHI_FACTORY_V2, abi=utils.SUSHI_FACTORY_ABI)
    pair_created_filter = sushi_contract.events.PairCreated.createFilter(fromBlock=13450360, toBlock=13450365)
    events = pair_created_filter.get_all_entries()
    print("Example response content:\n", events)
    
    event = events[0]
    token_address = utils.get_main_token_for_pair(event["args"]["token0"], event["args"]["token1"])
    ticker = utils.get_ticker_at_erc20(token_address)
    tweets, stats = utils.get_tweets("$" + ticker)
    print(token_address)
    print(ticker)
    print(stats)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(listen_for_ws_events_example())



