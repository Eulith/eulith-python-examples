import os
import sys

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

sys.path.insert(0, os.getcwd())
from utils.settings import PRIVATE_KEY, EULITH_REFRESH_TOKEN
from utils.banner import print_banner


"""
By default, Python only searches for modules and packages in predefined sets of directories, so we add current working
directory to beginning of system path to allow Python to find modules and packages that are located in the current
working directory when running the script using 'sys.path.insert(0, os.getcwd())'

Atomic/indivisible transactions are needed because suppose you want to swap one token for another on a decentralized
exchange that takes multiple steps such as approving the exchange contract to spend your tokens, checking the current
exchange rate, and actually executing the swap. To ensure that the swap is executed correctly, you would want to bundle
all of these steps together in a single atomic transaction, and if any step fails, the entire transaction is reverted
and all changes made in the transaction are rolled back. This ensures that the state of the system remains consistent
and that there are no partially executed transactions or incomplete operations that could lead to unexpected results.
"""

if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_REFRESH_TOKEN, construct_signing_middleware(wallet))

    ew3.v0.ensure_toolkit_contract(wallet.address)
    print("Creating smart contract if not exist...")

    print("Starting transactions...")
    ew3.v0.start_atomic_transaction(wallet.address)

    t1_send_amount_in_eth = 0.0001  # amount sending to first wallet in eth
    t2_send_amount_in_eth = 0.0001  # amount sending to second wallet in eth
    eth_needed = t1_send_amount_in_eth + t2_send_amount_in_eth
    t1_wallet_address = '0xFc11E697f23E5CbBeD3c59aC249955da57e57672'  # first wallet destination address
    t2_wallet_address = '0x47256A41027e94d1141Dd06f05DcB3ddE0421551'  # second wallet destination address

    source_wallet_balance = ew3.eth.get_balance(wallet.address) / 1e18  # convert to a float value from wei
    if source_wallet_balance < eth_needed + 0.002:  # we don't have enough ETH to complete the tx
        print(f'You have insufficient balance to run this example. Please fund the test wallet with '
              f'at least {eth_needed + 0.002} ETH')
        exit(1)

    print(
        f'Sending {eth_needed} ETH to transaction 1 wallet address {t1_wallet_address} and transaction 2 wallet address {t2_wallet_address}')

    try:
        ew3.eth.send_transaction({'from': wallet.address,
                                  'to': t1_wallet_address,
                                  'value': hex(int(t1_send_amount_in_eth * 1e18))})  # 1e18 converts value to gwei
        ew3.eth.send_transaction({'from': wallet.address,
                                  'to': t2_wallet_address,
                                  'value': hex(int(t2_send_amount_in_eth * 1e18))})
        atomic_tx = ew3.v0.commit_atomic_transaction()

    except Exception as e:
        print("Error: Failed to execute transactions or commit atomic transaction:", str(e))
        sys.exit(1)

    print("Sending atomic transaction as a whole and waiting for receipt...")

    try:
        tx_hash = ew3.eth.send_transaction(atomic_tx)
        receipt = ew3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"\nTransaction receipt: {receipt}")

        print(receipt)

    except web3.exceptions.TimeExhausted:
        print("Error: Transaction not found in the chain after 120 seconds. Try the atomic transaction again.")
        sys.exit(1)