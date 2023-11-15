import sys
import os

from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.requests import EulithShortOnRequest
from eulith_web3.signing import LocalSigner, construct_signing_middleware

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *

if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    with EulithWeb3('https://eth-main.eulithrpc.com/v0', EULITH_TOKEN, construct_signing_middleware(wallet)) as ew3:
        toolkit_address = ew3.v0.ensure_toolkit_contract(wallet.address)

        usdc = ew3.v0.get_erc_token(TokenSymbol.USDC)
        weth = ew3.v0.get_erc_token(TokenSymbol.WETH)

        collateral_amount = 5

        toolkit_balance = usdc.balance_of_float(toolkit_address)
        if toolkit_balance < collateral_amount * 1.05:
            # NOTE: moving funds to the toolkit contract is NOT necessary when using a Gnosis Safe, and therefore
            # is our recommendation for production trading
            print('Funding the toolkit contract to prepare for the short...')
            transfer_collateral_to_contract = usdc.transfer_float(toolkit_address, collateral_amount * 1.05,
                                                                  {'gas': 100000, 'from': wallet.address})
            ew3.eth.send_transaction(transfer_collateral_to_contract)

        short_on_params = EulithShortOnRequest(
            collateral_token=usdc,
            short_token=weth,
            collateral_amount=collateral_amount)

        ew3.v0.start_atomic_transaction(account=wallet.address)
        leverage = ew3.v0.short_on(short_on_params)

        print(f'Short leverage: {leverage}')

        # Example tx: https://etherscan.io/tx/0x836cc827e417c066c17bf92032fab0507172a9ac4ca030059bbe9d584804c222
        tx = ew3.v0.commit_atomic_transaction()
        tx['gas'] = 1000000
        tx_hash = ew3.eth.send_transaction(tx)

        r = ew3.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Short tx hash: {r["transactionHash"].hex()}')
