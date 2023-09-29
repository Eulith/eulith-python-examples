import os
import sys
import threading
import time
from typing import Dict

from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.uniswap import EulithUniswapPoolLookupRequest, UniswapPoolFee
from eulith_web3.websocket import EulithWebsocketRequestHandler

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *


class MyCustomStreamHandler(EulithWebsocketRequestHandler):
    def __init__(self, ew3):
        self.ew3 = ew3

    def handle_result(self, message: Dict):
        result = message.get('result', {})
        if type(result) == dict:
            data = result.get('data', None)
            sub_id = result.get('subscription', None)
            if data and sub_id:
                price = data.get('price', None)
                block_number = data.get('block_number')

                print(f'Received price {price} at block {block_number}')

    def handle_error(self, message: Dict):
        print(f'received an error {message}')


if __name__ == '__main__':
    print_banner()

    with EulithWeb3('https://eth-main.eulithrpc.com/v0', EULITH_TOKEN) as ew3:
        weth = ew3.v0.get_erc_token(TokenSymbol.WETH)
        usdc = ew3.v0.get_erc_token(TokenSymbol.USDC)

        pool_lookup_usdc_weth = EulithUniswapPoolLookupRequest(
            token_a=weth,
            token_b=usdc,
            fee=UniswapPoolFee.FiveBips
        )

        weth_usdc_pool = ew3.v0.get_univ3_pool(pool_lookup_usdc_weth)

        handler = MyCustomStreamHandler(ew3)

        subscribe_thread = threading.Thread(target=weth_usdc_pool.subscribe_prices, args=(handler,), daemon=True)
        subscribe_thread.start()

        while True:
            # Just want to keep the program alive to show the subscription prices coming in
            time.sleep(1)
