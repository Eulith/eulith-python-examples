import os
import sys

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

sys.path.insert(0, os.getcwd())
from utils.settings import PRIVATE_KEY, EULITH_TOKEN
from utils.banner import print_banner


"""
Atomic/indivisible transactions allow you to execute multiple legs of a trade as a single unit.

Enforced by code, an atomic transaction cannot execute partially. It must execute fully or not at all. This is a
broadly useful primitive, including in the case of a multi-leg trade where you don't want to get half way through
and not be able to finish the transaction.
"""

if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)

    with EulithWeb3("https://poly-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet)) as ew3:

        print("Creating execution contract if not exist...")
        ew3.v0.ensure_toolkit_contract(wallet.address)

        print("Starting atomic transaction\n")
        ew3.v0.start_atomic_transaction(wallet.address)

        t1_send_amount_in_eth = 0.0001  # amount sending to first wallet in eth
        t2_send_amount_in_eth = 0.0001  # amount sending to second wallet in eth
        eth_needed = t1_send_amount_in_eth + t2_send_amount_in_eth
        t1_wallet_address = '0xFc11E697f23E5CbBeD3c59aC249955da57e57672'  # first wallet destination address
        t2_wallet_address = '0x47256A41027e94d1141Dd06f05DcB3ddE0421551'  # second wallet destination address

        source_wallet_balance = ew3.eth.get_balance(wallet.address) / 1e18  # convert to a float value from wei
        if source_wallet_balance < eth_needed + 0.003:  # we don't have enough ETH to complete the tx
            print(f'\nYou have insufficient balance to run this example. Please fund the test wallet'
                  f' ({wallet.address}) with '
                  f'at least {eth_needed + 0.003} ETH/MATIC\n')
            exit(1)

        print(f'Sending {eth_needed} ETH to transaction 1 wallet address {t1_wallet_address} and '
              f'transaction 2 wallet address {t2_wallet_address}')

        try:
            ew3.eth.send_transaction({'from': wallet.address,
                                      'to': t1_wallet_address,
                                      'value': hex(int(t1_send_amount_in_eth * 1e18))})  # 1e18 converts value to wei
            ew3.eth.send_transaction({'from': wallet.address,
                                      'to': t2_wallet_address,
                                      'value': hex(int(t2_send_amount_in_eth * 1e18))})
            atomic_tx = ew3.v0.commit_atomic_transaction()
        except Exception as e:
            print("Error: Failed to execute transactions or commit atomic transaction:", str(e))
            exit(1)

        print("Sending atomic transaction as a whole and waiting for receipt...")

        try:
            tx_hash = ew3.eth.send_transaction(atomic_tx)
            receipt = ew3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"\nTransaction hash: {receipt['transactionHash'].hex()}")
        except web3.exceptions.TimeExhausted:
            print("Error: Transaction not found in the chain after 120 seconds. Try the atomic transaction again.")
            exit(1)
