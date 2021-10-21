

# subscribe to event log for sushi pairs created
    # requires
    # - infura (probably not geth light)
    # - 

# parse the created pair ticker from the event

# submit the ticker prefixed with "$" to twitter API
    # https://developer.twitter.com/en/docs/twitter-api/metrics
    # https://developer.twitter.com/en/docs/twitter-api/tweets/counts/introduction


from web3 import Web3
from eth_abi import decode_single
import json
import urllib
import time
from private import twitter_v1_api_keys, infura_api
from twitter import * 

w3 = Web3(Web3.HTTPProvider(infura_api.INFURA_HTTP))


SUSHI_FACTORY_V2 = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
SUSHI_FACTORY_ABI = json.loads(open("abi/abi_sushi_v2.json").read())["result"]

USDT_CONTRACT = Web3.toChecksumAddress("0x26d0ee7d0fad46b0deb495fa09e283151438c102")
USDC_CONTRACT = Web3.toChecksumAddress("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
WETH_CONTRACT = Web3.toChecksumAddress("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

PAIR_BASE_CONTRACTS = [USDC_CONTRACT, USDT_CONTRACT, WETH_CONTRACT]

ERC20_ABI = json.loads(open("abi/abi_erc20.json").read())["result"]

t = Twitter(auth=OAuth2(bearer_token=twitter_v1_api_keys.BEARER))


def get_tweets(query):
    tweets = []
    next_max_id = None
    query = query + " exclude:retweets"

    for _ in range(30):
        try:
            batch = t.search.tweets(q=query, count=100, max_id=next_max_id)
        except urllib.error.HTTPError:
            time.sleep(5)
            batch = t.search.tweets(q=query, count=100, max_id=next_max_id)

        batch_length = len(batch["statuses"])
        print("Batch of length", batch_length)
        if batch_length == 0:
            break
            
        next_max_id = batch["statuses"][-1]["id"] - 1

        for status in batch["statuses"]:
            tweets.append(
                {
                    "id": status["id"],
                    "text": status["text"],
                    "favorites": status["favorite_count"],
                    "retweets": status["retweet_count"],
                    "created_at": status["created_at"],
                    "username": status["user"]["screen_name"],
                    "followers": status["user"]["followers_count"],
                }
            )

    if len(tweets) == 0:
        return [], {}

    stats = {
        "all_tweets": len(tweets),
        "all_favorites": sum([s["favorites"] for s in tweets]),
        "avg_favorites": sum([s["favorites"] for s in tweets]) / len(tweets),
        "max_favorites": max([s["favorites"] for s in tweets]),
        "all_retweets": sum([s["retweets"] for s in tweets]),
        "avg_retweets": sum([s["retweets"] for s in tweets]) / len(tweets),
        "max_retweets": max([s["retweets"] for s in tweets]),
    }

    stats["max_rt_id"] = [s["id"] for s in tweets if s["retweets"] == stats["max_retweets"]][0]
    stats["max_fav_id"] = [s["id"] for s in tweets if s["favorites"] == stats["max_favorites"]][0]

    return tweets, stats

def get_ticker_at_erc20(address):
    contract = w3.eth.contract(address=address, abi=ERC20_ABI)
    ticker = contract.functions.symbol().call()
    print("Ticker for newly initialized liquidity pool:", ticker)
    return ticker

def get_main_token_for_pair(token0, token1):
    if token0 not in PAIR_BASE_CONTRACTS:
        return token0
    return token1

def decode_PairCreated(message):
    return list(decode_single(
        "(address,address,address,uint256)",
        bytearray.fromhex(json.loads(message)["params"]["result"]["data"][2:])
    ))
