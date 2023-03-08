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


def get_0x_gas_cost_in_gwei():
    endpoint = "https://api.0x.org/swap/v1/quote"
    params = {
        "sellToken": "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
        "buyToken": "0xb9871cB10738eADA636432E86FC0Cb920Dc3De24",
        "sellAmount": "1000000000000000000"
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    gas_price = data["gasPrice"]
    gas_limit = data["gas"]
    WEI_AND_GWEI_CONVERSION_RATE = 1e9
    gas_cost_in_gwei = (int(gas_price) * int(gas_limit)) / WEI_AND_GWEI_CONVERSION_RATE
    return gas_cost_in_gwei


def get_1inch_gas_cost_in_gwei():
    endpoint = "https://api.1inch.io/v5.0/1/swap"
    params = {
        "fromTokenAddress": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "toTokenAddress": "0x111111111117dc0aa78b770fa6a738034120c302",
        "amount": "10000000000000000",
        "fromAddress": "0xBAFe448C52BFA4C64bA9671DF5ceb3bE1188b962",
        "slippage": "1"
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    gas_price = int(data["tx"]["gasPrice"])
    gas_limit = int(data["tx"]["gas"])

    WEI_AND_GWEI_CONVERSION_RATE = 1e9
    gas_cost_in_gwei = (gas_price * gas_limit) / WEI_AND_GWEI_CONVERSION_RATE
    return gas_cost_in_gwei


if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_REFRESH_TOKEN, construct_signing_middleware(wallet))

    print("Refreshing User Data")
    ew3.v0.ensure_valid_api_token()
    print("The API token has been refreshed.")

    toolkit_contract_address = ew3.v0.ensure_toolkit_contract(wallet.address)
    print(f"The proxy contract address is: {toolkit_contract_address}")

    source_wallet_balance = ew3.eth.get_balance(wallet.address) / 1e18
    print(f"The wallet {wallet.address} balance is: {source_wallet_balance} eth")

    GWEI_AND_ETH_CONVERSION = 1e9
    zerox_aggregator_gas_cost = get_0x_gas_cost_in_gwei()
    print(f"If aggregator = 0x, max gas cost = {zerox_aggregator_gas_cost/GWEI_AND_ETH_CONVERSION} eth")

    oneinch_gas_cost = get_1inch_gas_cost_in_gwei()
    print(f"If aggregator = 1inch, max gas cost = {oneinch_gas_cost/GWEI_AND_ETH_CONVERSION} eth")


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

    weth = ew3.eulith_get_erc_token(TokenSymbol.WETH)
    usdt = ew3.eulith_get_erc_token(TokenSymbol.USDT)
    usdc = ew3.eulith_get_erc_token(TokenSymbol.USDC)
    link = ew3.eulith_get_erc_token(TokenSymbol.LINK)
    matic = ew3.eulith_get_erc_token(TokenSymbol.MATIC)
    bnb = ew3.eulith_get_erc_token(TokenSymbol.BNB)
    busd = ew3.eulith_get_erc_token(TokenSymbol.BUSD)
    steth = ew3.eulith_get_erc_token(TokenSymbol.STETH)
    matic = ew3.eulith_get_erc_token(TokenSymbol.MATIC)
    ldo = ew3.eulith_get_erc_token(TokenSymbol.LDO)
    crv = ew3.eulith_get_erc_token(TokenSymbol.CRV)
    cvx = ew3.eulith_get_erc_token(TokenSymbol.CVX)
    badger = ew3.eulith_get_erc_token(TokenSymbol.BADGER)
    bal = ew3.eulith_get_erc_token(TokenSymbol.BAL)
    oneinch = ew3.eulith_get_erc_token(TokenSymbol.ONEINCH)
    uni = ew3.eulith_get_erc_token(TokenSymbol.UNI)
    ape = ew3.eulith_get_erc_token(TokenSymbol.APE)
    gmt = ew3.eulith_get_erc_token(TokenSymbol.GMT)

    SELL_TOKEN = usdc
    BUY_TOKEN = weth
    SELL_AMOUNT = 10
    slippage_tolerance = 1

    tokens = [weth, usdt, usdc, matic, bnb, busd, steth, ldo, crv, cvx, badger, bal, oneinch, uni, ape, gmt]
    print(f"For the SELL_TOKEN {SELL_TOKEN.symbol} and the BUY_TOKEN {BUY_TOKEN.symbol} and a slippage tolerance set to "
          f"{slippage_tolerance}%, returning live market data")

    market_data = []

    for token in tokens:
        if token == SELL_TOKEN:
            continue
        prices = {}
        for dex in dexs:
            swap_params = EulithSwapRequest(
                sell_token=SELL_TOKEN,
                buy_token=token,
                sell_amount=SELL_AMOUNT,
                liquidity_source=dex,
                recipient=ew3.eulith_contract_address(wallet.address),
                slippage_tolerance=slippage_tolerance
            )

            try:
                price, txs = ew3.eulith_swap_quote(swap_params)
                print(f"Price for {token.symbol} on {dex}: {price:.4f}")
                prices[dex] = price
            except EulithRpcException as e:
                # print(f"Error occurred while getting price from {dex.name} for {token.symbol}. Error: {e}")
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
