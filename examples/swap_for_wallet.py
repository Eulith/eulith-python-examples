import os
import sys

from eulith_web3.eulith_web3 import *
from eulith_web3.ledger import LedgerSigner
from eulith_web3.signing import construct_signing_middleware

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *
from utils.common import check_wallet_balance

if __name__ == '__main__':
    """
    You can select which network you would like to operate on by changing the subdomain of the Eulith RPC
    endpoint https://eth-main.eulithrpc.com/v0. For example, you might want to execute on Arbitrum. 
    In that case, you should use https://arb-main.eulithrpc.com/v0
    """

    print_banner()

    # ATTENTION: You made need to change this wallet depending on what type of wallet you're using.
    wallet = LedgerSigner()

    with EulithWeb3("https://arb-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet)) as ew3:
        check_wallet_balance(ew3, 0.02)

        print('Starting swap example...\n')

        weth = ew3.eulith_get_erc_token(TokenSymbol.WETH)
        usdc = ew3.eulith_get_erc_token(TokenSymbol.USDC)

        amount = 0.001

        swap = EulithSwapRequest(
            sell_token=weth,
            buy_token=usdc,
            sell_amount=amount,
            recipient=wallet.address)

        price, txs = ew3.v0.get_swap_quote(swap)

        print(f'Swapping at price: {1 / round(price, 5)} USDC per WETH')
        print('Please check your connected wallet (if applicable) to confirm the transactions')

        receipt = ew3.v0.send_multi_transaction(txs)

        print(f"Final transaction hash: {receipt.get('transactionHash').hex()}")
