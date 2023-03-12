import os
import sys
import statistics

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner
from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3

sys.path.insert(0, os.getcwd())
from utils.settings import PRIVATE_KEY, EULITH_REFRESH_TOKEN
from utils.banner import print_banner


if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_REFRESH_TOKEN, construct_signing_middleware(wallet))

    print("\n\nRETRIEVING CURRENT LIVE MARKET DATA...")

    dexs = [EulithLiquiditySource.UNISWAP_V3,
            EulithLiquiditySource.BALANCER_V2,
            EulithLiquiditySource.SUSHI,
            EulithLiquiditySource.COMPOUND,
            EulithLiquiditySource.PANCAKE,
            EulithLiquiditySource.CURVE_V2,
            EulithLiquiditySource.CURVE_V1,
            EulithLiquiditySource.SADDLE,
            EulithLiquiditySource.SYNAPSE,
            EulithLiquiditySource.BALANCER_V1]


    weth = ew3.v0.get_erc_token(TokenSymbol.WETH)
    usdt = ew3.v0.get_erc_token(TokenSymbol.USDT)
    usdc = ew3.v0.get_erc_token(TokenSymbol.USDC)
    link = ew3.v0.get_erc_token(TokenSymbol.LINK)
    matic = ew3.v0.get_erc_token(TokenSymbol.MATIC)
    bnb = ew3.v0.get_erc_token(TokenSymbol.BNB)
    busd = ew3.v0.get_erc_token(TokenSymbol.BUSD)
    steth = ew3.v0.get_erc_token(TokenSymbol.STETH)
    matic = ew3.v0.get_erc_token(TokenSymbol.MATIC)
    ldo = ew3.v0.get_erc_token(TokenSymbol.LDO)
    crv = ew3.v0.get_erc_token(TokenSymbol.CRV)
    cvx = ew3.v0.get_erc_token(TokenSymbol.CVX)
    badger = ew3.v0.get_erc_token(TokenSymbol.BADGER)
    bal = ew3.v0.get_erc_token(TokenSymbol.BAL)
    oneinch = ew3.v0.get_erc_token(TokenSymbol.ONEINCH)
    uni = ew3.v0.get_erc_token(TokenSymbol.UNI)
    ape = ew3.v0.get_erc_token(TokenSymbol.APE)
    gmt = ew3.v0.get_erc_token(TokenSymbol.GMT)

    SELL_TOKEN = usdc
    SELL_AMOUNT = 10
    SLIPPAGE_TOLERANCE = 1

    tokens = [weth, usdt, usdc, matic, bnb, busd, steth, ldo, crv, cvx, badger, bal, oneinch, uni, ape, gmt]

    market_data = []

    # for the same sell token usdc, we are iterating to see respective swap prices for the buy tokens in the tokens list
    for token in tokens:
        if token == SELL_TOKEN:
            continue

        prices = {}

        print(f"\nFor the SELL_TOKEN {SELL_TOKEN.symbol} and the BUY_TOKEN {token.symbol} and a slippage tolerance set "
              f"to {SLIPPAGE_TOLERANCE}%, returning live market data")

        for dex in dexs:
            swap_params = EulithSwapRequest(
                sell_token=SELL_TOKEN,
                buy_token=token,
                sell_amount=SELL_AMOUNT,
                liquidity_source=dex,
                slippage_tolerance=SLIPPAGE_TOLERANCE
            )

            try:
                price, txs = ew3.v0.get_swap_quote(swap_params)
                print(f"Price for {token.symbol} on {dex}: {price:.4f} USDC")
                prices[dex] = price
            except EulithRpcException as e:
                # If insufficient liquidity at the dex, we skip and try the next one
                continue

        if prices:
            max_price_dex = max(prices, key=prices.get)
            min_price_dex = min(prices, key=prices.get)
            max_price = prices[max_price_dex]
            min_price = prices[min_price_dex]
            average_price = statistics.mean(prices.values())
            spread = (max_price - min_price) / min_price
            market_data.append({
                'token': token.symbol,
                'prices': prices,
                'max_price': max_price,
                'min_price': min_price,
                'max_price_dex': max_price_dex,
                'min_price_dex': min_price_dex,
                'average_price': average_price,
                'spread': spread
            })

    if market_data:
        for data in market_data:
            print(f"{data['token']}:")
            print(f"\tMax price: {data['max_price']:.4f} on {data['max_price_dex'].name}")
            print(f"\tMin price: {data['min_price']:.4f} on {data['min_price_dex'].name}")
            print(f"\tAverage price: {data['average_price']:.4f}")
            print(f"\tSpread: {data['spread']:.2%}")
            print("\tPrices by liquidity source:")
            for dex, price in data['prices'].items():
                print(f"\t\t{dex.name}: {price:.4f}")
    else:
        print("No valid prices obtained")
