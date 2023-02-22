import os
import sys

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *

if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_REFRESH_TOKEN, construct_signing_middleware(wallet))

    toolkit_contract_address = ew3.v0.ensure_toolkit_contract(wallet.address)

    print(f'Toolkit contract address is: {toolkit_contract_address}\n')

    weth = ew3.v0.get_erc_token(TokenSymbol.WETH)

    toolkit_weth_balance = weth.balance_of_float(toolkit_contract_address)
    wallet_weth_balance = weth.balance_of_float(wallet.address)

    print(f'Wallet WETH balance: {wallet_weth_balance}')
    print(f'Toolkit contract WETH balance: {toolkit_weth_balance}\n')

    print(f'WETH address: {weth.address}')
    print(f'WETH decimals: {weth.decimals}\n')

    if ew3.eth.get_balance(wallet.address) / 10 ** 18 < 0.01:
        print('Skipping example WETH deposit, insufficient balance in the wallet. Need at least 0.01 ETH')
    else:
        deposit_weth = weth.deposit_eth(0.001, {'from': wallet.address, 'gas': 100000})
        deposit_hash = ew3.eth.send_transaction(deposit_weth)
        print(f'WETH deposit tx hash: {deposit_hash.hex()}')
        ew3.eth.wait_for_transaction_receipt(deposit_hash)

        time.sleep(2)
        wallet_weth_balance = weth.balance_of_float(wallet.address)
        print(f'New Wallet WETH balance: {wallet_weth_balance}')
