import os
import sys

from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.signing import LocalSigner, construct_signing_middleware
from eulith_web3.uniswap import UniswapPoolFee, EulithUniswapPoolLookupRequest

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *

if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    with EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet)) as ew3:

        weth = ew3.v0.get_erc_token(TokenSymbol.WETH)
        usdc = ew3.v0.get_erc_token(TokenSymbol.USDC)

        pool_fee = UniswapPoolFee.FiveBips

        target_pool = ew3.v0.get_univ3_pool(EulithUniswapPoolLookupRequest(
            fee=pool_fee,
            token_a=weth,
            token_b=usdc
        ))

        # The volume of the transaction you're trying to front run
        pending_tx_volume = 1.5
        price_1, fee_1, request_details_pending = target_pool.get_quote(sell_token=weth, amount=pending_tx_volume)

        # The sqrt limit price AFTER the pending tx confirms
        after_pending_sqrt_limit = request_details_pending.get('sqrt_limit_price')
        print(f'After PENDING tx confirms sqrt limit: {after_pending_sqrt_limit}')

        your_target_volume = 10
        # Your transaction ahead of the pending tx
        total_volume = your_target_volume + pending_tx_volume
        price_2, fee_2, request_details_target = target_pool.get_quote(sell_token=weth, amount=total_volume)

        # The sqrt limit price AFTER your transaction confirms AND the pending tx confirms
        after_both_sqrt_limit = request_details_target.get('sqrt_limit_price')
        print(f'After BOTH txs confirms sqrt limit:   {after_both_sqrt_limit}')
