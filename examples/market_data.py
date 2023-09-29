import os
import sys
import statistics

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner
from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.swap import EulithLiquiditySource

sys.path.insert(0, os.getcwd())
from utils.settings import PRIVATE_KEY, EULITH_TOKEN
from utils.banner import print_banner


if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet))

    print("\n\nRetrieving live market data...")

    venues = [EulithLiquiditySource.UNISWAP_V3,
              EulithLiquiditySource.BALANCER_V2,
              EulithLiquiditySource.SUSHI,
              EulithLiquiditySource.COMPOUND,
              EulithLiquiditySource.PANCAKE,
              EulithLiquiditySource.CURVE_V2,
              EulithLiquiditySource.CURVE_V1,
              EulithLiquiditySource.SADDLE,
              EulithLiquiditySource.SYNAPSE,
              EulithLiquiditySource.BALANCER_V1]

    token_symbols = [TokenSymbol.WETH, TokenSymbol.USDT, TokenSymbol.LINK, TokenSymbol.MATIC, TokenSymbol.STETH]
    tokens = [ew3.v0.get_erc_token(t) for t in token_symbols]

    sell_amount = 10
    slippage_tolerance = 0.01
    sell_token = ew3.v0.get_erc_token(TokenSymbol.USDC)

    market_data = []

    for token in tokens:
        for dex in venues:
            swap_params = EulithSwapRequest(
                sell_token=sell_token,
                buy_token=token,
                sell_amount=sell_amount,
                liquidity_source=dex,
                slippage_tolerance=slippage_tolerance)

            try:
                price, txs = ew3.v0.get_swap_quote(swap_params)
                print(f"Price for {token.symbol} on {dex}: {price:.4f} USDC")
            except EulithRpcException as e:
                continue
    else:
        print("No valid prices obtained")
