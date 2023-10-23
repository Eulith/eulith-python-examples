import os
import sys

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *

if __name__ == '__main__':
    """
    Note this example requires you to have DeFi armor set up. You can do this through the frontend
    at https://eulithclient.com. Alternatively, please see https://github.com/Eulith/armor-cli for more instructions.
    
    You can also select which network you would like to operate on by changing the subdomain of the Eulith RPC
    endpoint https://eth-main.eulithrpc.com/v0. For example, you might want to execute on Arbitrum. 
    In that case, you should use https://arb-main.eulithrpc.com/v0
    """

    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    with EulithWeb3("https://arb-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet)) as ew3:
        if ew3.eth.get_balance(wallet.address) / 10 ** 18 < 0.03:
            print("Your wallet doesn't have enough balance to complete this example")
            print("Please deposit at least 0.02 ETH")
            exit(1)

        print('Starting swap example...\n')

        weth = ew3.eulith_get_erc_token(TokenSymbol.WETH)
        usdc = ew3.eulith_get_erc_token(TokenSymbol.USDC)

        amount = 2

        swap = EulithSwapRequest(
            sell_token=usdc,
            buy_token=weth,
            sell_amount=amount)

        armor, safe = ew3.v0.get_armor_and_safe_addresses(wallet.address)

        ew3.v0.start_atomic_transaction(wallet.address, gnosis=safe)

        price, _ = ew3.v0.get_swap_quote(swap)

        print(f'Swapping at price: {round(price, 5)} USDC per WETH')

        final_tx = ew3.v0.commit_atomic_transaction()
        rec = ew3.eth.send_transaction(final_tx)

        print(f"\nSwap tx hash: {rec.hex()}")
