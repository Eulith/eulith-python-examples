import os
import sys

from eulith_web3.signing import construct_signing_middleware, LocalSigner
from eulith_web3.eulith_web3 import *

sys.path.insert(0, os.getcwd())
from utils.settings import PRIVATE_KEY, EULITH_TOKEN
from utils.banner import print_banner


"""
Eulith DeFi RFQ returns a real-time executable quote for your given token pair and volume.

This quote is guaranteed to execute at the provided price, otherwise the transaction will revert.

You can optionally set a slippage parameter if you want to allow for more price movement at execution.
"""
if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)

    with EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet)) as ew3:
        # Look up the ERC20's you care about
        weth = ew3.v0.get_erc_token(TokenSymbol.WETH)
        usdc = ew3.v0.get_erc_token(TokenSymbol.USDC)

        ### ----------- Best Price ----------- ###
        swap = EulithSwapRequest(sell_token=weth, buy_token=usdc, sell_amount=10)
        price, txs = ew3.v0.get_swap_quote(swap)

        print(f'\n\nBest Price: {1 / price}\n\n')
