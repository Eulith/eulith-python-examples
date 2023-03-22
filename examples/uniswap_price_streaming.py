import json
import os
import sys
import time

from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.uniswap import EulithUniswapPoolLookupRequest, UniswapPoolFee

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *

if __name__ == '__main__':
    print_banner()

    ew3 = EulithWeb3('https://eth-main.eulithrpc.com/v0', EULITH_REFRESH_TOKEN)

    weth = ew3.v0.get_erc_token(TokenSymbol.WETH)
    usdc = ew3.v0.get_erc_token(TokenSymbol.USDC)

    pool_lookup_parameters = EulithUniswapPoolLookupRequest(
        token_a=weth,
        token_b=usdc,
        fee=UniswapPoolFee.FiveBips
    )

    weth_usdc_pool = ew3.v0.get_univ3_pool(pool_lookup_parameters)

    def new_price_handler(websocket_connection, message, eulith_web3):
        dict_message = json.loads(message)
        result = dict_message.get('result', {})
        if type(result) == dict:
            price = result.get('data', {}).get('price', None)
            if price:
                print(f'New USDC/WETH price: {price}')

    def error_handler(websocket_connection, error, eulith_web3):
        print(f'Got an error: {error}')

    subscription_handle = weth_usdc_pool.subscribe_prices(new_price_handler, error_handler)

    time.sleep(60)

    subscription_handle.unsubscribe()
    ew3.websocket_conn.disconnect()
