import os
import sys

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner
from eulith_web3.swap import EulithSwapProvider

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *

if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet))

    if ew3.eth.get_balance(wallet.address) / 10 ** 18 < 0.03:
        print("Your wallet doesn't have enough balance to complete this example")
        print("Please deposit at least 0.02 ETH")

    print('Starting swap example...\n')

    weth = ew3.eulith_get_erc_token(TokenSymbol.WETH)
    usdt = ew3.eulith_get_erc_token(TokenSymbol.USDT)
    usdc = ew3.eulith_get_erc_token(TokenSymbol.USDC)

    amount = 0.005

    swap = EulithSwapRequest(
        sell_token=weth,
        buy_token=usdc,
        sell_amount=amount,
        recipient=wallet.address,
        route_through=EulithSwapProvider.ONE_INCH)

    toolkit_address = ew3.v0.ensure_toolkit_contract(wallet.address)
    toolkit_sell_token_balance = weth.balance_of_float(toolkit_address)

    if toolkit_sell_token_balance < amount:
        deposit_tx = weth.deposit_eth(amount, {'from': wallet.address, 'gas': 100000})
        deposit_hash = ew3.eth.send_transaction(deposit_tx)
        print(f'Converting ETH to WETH: {deposit_hash.hex()}')
        ew3.eth.wait_for_transaction_receipt(deposit_hash)

        transfer_to_toolkit_contract = weth.transfer_float(
            toolkit_address, amount, {'from': wallet.address, 'gas': 100000})
        transfer_hash = ew3.eth.send_transaction(transfer_to_toolkit_contract)
        print(f'Sending enough WETH to the toolkit contract to cover the swap: {transfer_hash.hex()}')
        ew3.eth.wait_for_transaction_receipt(transfer_hash)

    ew3.v0.start_atomic_transaction(wallet.address)
    price, txs = ew3.v0.get_swap_quote(swap)

    print(f'Swapping at price: {round(price, 5)} WETH per USDC')

    ew3.v0.send_multi_transaction(txs)

    final_tx = ew3.v0.commit_atomic_transaction()
    rec = ew3.eth.send_transaction(final_tx)

    print(f"\nSwap tx hash: {rec.hex()}")
