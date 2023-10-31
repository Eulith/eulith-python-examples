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
    with EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet)) as ew3:
        weth = ew3.v0.get_erc_token(TokenSymbol.WETH)

        wallet_weth_balance = weth.balance_of_float(wallet.address)

        print(f'Wallet WETH balance: {wallet_weth_balance}')
