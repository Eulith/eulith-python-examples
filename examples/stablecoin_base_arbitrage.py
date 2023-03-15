import os
import sys

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

sys.path.insert(0, os.getcwd())
from utils.settings import PRIVATE_KEY, EULITH_REFRESH_TOKEN
from utils.banner import print_banner

if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_REFRESH_TOKEN, construct_signing_middleware(wallet))

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

    MIDDLE_UNIT_CONVERSION = 1e9
    SLIPPAGE_TOLERANCE = 0
    SELL_TOKEN_DECIMALS = 1e6
    SELL_TOKEN = usdc
    SELL_AMOUNT = 100
    MIN_PROFIT_THRESHOLD = 0  # minimum profit as a numeric amount
    tokens = [weth, usdt, usdc, matic, busd, steth, ldo, crv, cvx, badger, bal, oneinch, uni, ape]
    profitable_trades = []

    # _______________________________________________________________________________________________________________
    # Setting up toolkit/proxy contract
    ew3.v0.ensure_toolkit_contract(wallet.address)
    proxy_contract_address = ew3.eulith_contract_address(wallet.address)
    sell_token_proxy_balance = SELL_TOKEN.balance_of(proxy_contract_address)
    sell_token_proxy_balance = sell_token_proxy_balance/SELL_TOKEN_DECIMALS

    if sell_token_proxy_balance < SELL_AMOUNT:
        print(f"Funding toolkit contract...")
        if SELL_TOKEN.address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2":  # WETH address
            print("Sell token address is WETH, converting ETH to WETH")
            eth_to_weth_tx = weth.deposit_wei(int(SELL_AMOUNT*SELL_TOKEN_DECIMALS))
            eth_to_weth_tx['from'] = wallet.address
            rec = ew3.eth.send_transaction(eth_to_weth_tx)
            receipt = ew3.eth.wait_for_transaction_receipt(rec)

        amount_to_send_in_sell_token = SELL_AMOUNT - sell_token_proxy_balance
        transfer_tx = SELL_TOKEN.transfer(proxy_contract_address, int(amount_to_send_in_sell_token),
                                          override_tx_parameters = {'from': wallet.address})
        rec = ew3.eth.send_transaction(transfer_tx)
        receipt = ew3.eth.wait_for_transaction_receipt(rec)
        print(f"Proxy contract {proxy_contract_address} funded with {amount_to_send_in_sell_token} {SELL_TOKEN}, "
              f"receipt is: {receipt['transactionHash'].hex()}")

    # _______________________________________________________________________________________________________________
    # Finding profitable arbitrage opportunities with base USDC as SELL_TOKEN
    for token in tokens:
        if token == SELL_TOKEN:
            continue
        prices = {}
        max_price = None
        min_price = None
        print(f"\nFor SELL_TOKEN {SELL_TOKEN.symbol}, BUY_TOKEN {token.symbol}, slippage set to {SLIPPAGE_TOLERANCE}%")

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
                print(f"Price for {token.symbol} on {dex}: {price:.4f} is USDC")
                prices[dex] = price
                if max_price is None or price > max_price:
                    max_price = price
                if min_price is None or price < min_price:
                    min_price = price
            except EulithRpcException as e:
                continue

        if prices:
            max_price_dex = max(prices, key=prices.get)
            min_price_dex = min(prices, key=prices.get)
            max_price = prices[max_price_dex]
            min_price = prices[min_price_dex]
            print(max_price,min_price)
            aggregator = EulithSwapProvider.ONE_INCH
            if aggregator == EulithSwapProvider.ZERO_EX:
                gas_usage = 800000
            elif aggregator == EulithSwapProvider.ONE_INCH:
                gas_usage = 450000

            gas_cost_in_eth = (ew3.eth.gas_price * gas_usage) / 1e18
            swap_params = EulithSwapRequest(
                sell_token=SELL_TOKEN,
                buy_token=weth,
                sell_amount=1.0)

            sell_token_to_eth_price, txs = ew3.eulith_swap_quote(swap_params)
            gas_cost_in_sell_token = gas_cost_in_eth*sell_token_to_eth_price
            spread = SELL_AMOUNT*((max_price - min_price) / min_price)
            profit = spread - gas_cost_in_sell_token

            if profit > MIN_PROFIT_THRESHOLD:
                profitable_trade = {'token': token, 'profit': profit}
                profitable_trades.append(profitable_trade)

    # _______________________________________________________________________________________________________________
    # SUBMITTING PROFITABLE ARBITRAGE
    # We submit the most profitable trade for execution, however you can print and index the profitable_trades
    # dictionary for more selection
    if profitable_trades:
        best_trade = max(profitable_trades, key=lambda x: x['profit'])
        token_to_buy = best_trade['token']
        print(f"Best trade: selling {SELL_AMOUNT} {SELL_TOKEN.symbol}, buying {token_to_buy.symbol} for "
              f"{best_trade['profit']:.2f} USDC profit")

        ew3.v0.start_atomic_transaction(wallet.address)
        swap = EulithSwapRequest(
            sell_token=SELL_TOKEN,
            buy_token=token_to_buy,
            sell_amount=SELL_AMOUNT,
            recipient=ew3.eulith_contract_address(wallet.address),
            route_through=aggregator)
        price, buy_txs = ew3.v0.get_swap_quote(swap)
        ew3.v0.send_multi_transaction(buy_txs)

        swap = EulithSwapRequest(
            sell_token=token_to_buy,
            buy_token=SELL_TOKEN,
            sell_amount=SELL_AMOUNT,
            recipient=wallet.address,
            route_through=aggregator)
        price, sell_txs = ew3.v0.get_swap_quote(swap)
        ew3.v0.send_multi_transaction(sell_txs)

        pending_block_base_fee = ew3.eth.get_block('pending').baseFeePerGas / MIDDLE_UNIT_CONVERSION
        next_block_max_base_fee = pending_block_base_fee * 1.25
        priority_fee = abs(next_block_max_base_fee - pending_block_base_fee)

        final_tx = ew3.v0.commit_atomic_transaction()
        final_tx['maxFeePerGas'] = int(ew3.eth.gas_price)
        final_tx['maxPriorityFeePerGas'] = priority_fee * MIDDLE_UNIT_CONVERSION
        final_tx['gas'] = gas_usage

        tx = ew3.eth.send_transaction(final_tx)
        receipt = ew3.eth.wait_for_transaction_receipt(tx)
        print(f"Atomic arbitrage transaction executed, receipt: {receipt['transactionHash'].hex()}")