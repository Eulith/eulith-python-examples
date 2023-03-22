import datetime
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

    pool_lookup_usdc_weth = EulithUniswapPoolLookupRequest(
        token_a=weth,
        token_b=usdc,
        fee=UniswapPoolFee.FiveBips
    )

    weth_usdc_pool = ew3.v0.get_univ3_pool(pool_lookup_usdc_weth)

    with open('usdc_weth_prices.csv', 'w+') as file:
        file.write('timestamp,block_number,price\n')

    def new_price_handler(websocket_connection, message, eulith_web3):
        dict_message = json.loads(message)
        result = dict_message.get('result', {})
        if type(result) == dict:
            data = result.get('data', None)
            sub_id = result.get('subscription', None)
            if data and sub_id:
                price = data.get('price', None)
                time_now = int(time.mktime(datetime.datetime.now().timetuple()))  # current unix timestamp
                block_number = data.get('block_number')

                if ew3.sub_to_file:
                    file_name = eulith_web3.sub_to_file[sub_id]
                    print(f'writing new price to {file_name}')
                    with open(file_name, 'a') as file:
                        file.write(f'{time_now},{block_number},{price}\n')


    def error_handler(websocket_connection, error, eulith_web3):
        print(f'Got an error: {error}')

    usdc_weth = weth_usdc_pool.subscribe_prices(new_price_handler, error_handler)

    ew3.sub_to_file = None

    # waiting for a subscription ID to come back from the server,
    # so we can appropriately index on the correct filename
    while not usdc_weth.sub_id:
        time.sleep(0.2)

    ew3.sub_to_file = {
        usdc_weth.sub_id: 'usdc_weth_prices.csv',
    }
