import os
import sys

from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.signing import LocalSigner, construct_signing_middleware

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *

if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet))

    wallet_balance = ew3.eth.get_balance(wallet.address) / 10 ** 18
    if wallet_balance < 0.008:
        print(f'Insufficient wallet balance to run the example. '
              f'Please send at least 0.01 ETH to {wallet.address} to continue')
        exit(1)

    toolkit_contract_address = ew3.v0.ensure_toolkit_contract(wallet.address)
    print(f'Toolkit contract wallet address: {toolkit_contract_address}\n')

    weth = ew3.v0.get_erc_token(TokenSymbol.WETH)
    withdraw_amount = 0.001

    weth_toolkit_balance = weth.balance_of_float(toolkit_contract_address)
    print(f'Toolkit contract WETH balance: {weth_toolkit_balance}')

    if weth_toolkit_balance < withdraw_amount:
        print('The toolkit contract doesnt have sufficient WETH to demonstrate the withdraw. '
              f'Please send 0.001 WETH to {toolkit_contract_address} to continue')
        exit(1)

    # Going to approve our wallet inside an atomic tx so that our wallet is free to call transfer_from
    # on the toolkit contract. Within an atomic tx, msg.sender is the toolkit contract (NOT your wallet)
    ew3.v0.start_atomic_transaction(wallet.address)

    approval_tx = weth.approve_float(wallet.address, withdraw_amount)
    ew3.eth.send_transaction(approval_tx)

    atomic_tx = ew3.v0.commit_atomic_transaction()
    tx_hash = ew3.eth.send_transaction(atomic_tx)
    print(f'Approve wallet from the toolkit contract tx: {tx_hash.hex()}')
    ew3.eth.wait_for_transaction_receipt(tx_hash)

    withdraw_weth_from_toolkit_tx = weth.transfer_from_float(
        toolkit_contract_address, wallet.address, withdraw_amount, {'from': wallet.address, 'gas': 100000})
    tx_hash = ew3.eth.send_transaction(withdraw_weth_from_toolkit_tx)
    print(f'Withdraw tx: {tx_hash.hex()}')
