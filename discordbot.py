from private import discord_keys, infura_api
import utils

import traceback
import websockets
import asyncio
import json

import discord
from discord.ext import commands
from discord.ext.commands import bot

def format_liquidity_pool_created_alert(ticker, underlying, stats):
    return f"""
@here
```
Liquidity Pool Created: {ticker}/{underlying}

{ticker} mentioned in {stats["all_tweets"]} tweets

Total favorites: {stats["all_favorites"]}
Most favorites: {stats["max_favorites"]} twitter.com/i/status/{stats["max_fav_id"]}

Total RTs: {stats["all_retweets"]}
Most RTs: {stats["max_retweets"]} twitter.com/i/status/{stats["max_rt_id"]}
```
:eyes: to watch liquidity
:white_check_mark: to automate entry
"""


class UnfairLaunchBot(bot.BotBase, discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = None
        asyncio.run_coroutine_threadsafe(self.sushi_monitor(), self.loop)

    async def on_ready(self):
        print(self.user)
        self.channel = self.get_channel(discord_keys.UNFAIR_CHANNEL)

    async def sushi_monitor(self):
        await self.wait_until_ready()
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

            while not self.is_closed():
                try:
                    event = await ws.recv()
                    await self.handle(event)
                except Exception:
                    traceback.print_exc() 

    async def handle(self, event):
        event = json.loads(event)
        print(event)
        token0 = utils.w3.toChecksumAddress(event["result"]["topics"][1][26:])
        token1 = utils.w3.toChecksumAddress(event["result"]["topics"][2][26:])
        token = utils.get_main_token_for_pair(token0, token1)
        ticker = utils.get_ticker_at_erc20(token)
        tweets, stats = utils.get_tweets("$" + ticker)
        await self.channel.send(format_liquidity_pool_created_alert(ticker, "USDC", stats))
        


b = UnfairLaunchBot(command_prefix="!")

@b.command()
async def test(ctx):
    await ctx.send("hello")

b.run(discord_keys.DISCORD_BOT_KEY)

