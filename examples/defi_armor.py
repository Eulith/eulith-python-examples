"""
NOTE: in order to run.sh this example, you must have a correctly configured KMS key with AWS credentials in your ~/.aws
directory. See https://www.loom.com/share/6cf2ba73f14847758f1551223cbe7a28, or get in touch with us for help with this.
"""
import os
import sys

import boto3

from eulith_web3.erc20 import EulithERC20, TokenSymbol, EulithWETH
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.kms import KmsSigner
from eulith_web3.signing import LocalSigner, construct_signing_middleware
from eulith_web3.contract_bindings.safe.i_safe import ISafe

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import EULITH_REFRESH_TOKEN

EULITH_URL = "https://eth-main.eulithrpc.com/v0"

AWS_CREDENTIALS_PROFILE_NAME = "default"

WETH_AMOUNT = 0.0000001


def defi_armor():
    print_banner()

    # Retrieve our keys from AWS.
    session = boto3.Session(profile_name=AWS_CREDENTIALS_PROFILE_NAME)
    wallet = get_kms_key(session, "ARMOR_AUTH_ADDRESS")
    owner1 = get_kms_key(session, "ARMOR_OWNER1")
    owner2 = get_kms_key(session, "ARMOR_OWNER2")
    owner3 = get_kms_key(session, "ARMOR_OWNER3")
    safe_owners = [owner1, owner2, owner3]

    print()
    print("/*** initializing keys ***\\")
    print(f"==> wallet address:  {wallet.address}")
    print(f"==> owner 1 address: {owner1.address}")
    print(f"==> owner 2 address: {owner2.address}")
    print(f"==> owner 3 address: {owner3.address}")

    # Initialize the Eulith Python client.
    ew3 = EulithWeb3(
        eulith_url=EULITH_URL,
        eulith_refresh_token=EULITH_REFRESH_TOKEN,
        signing_middle_ware=construct_signing_middleware(wallet),
    )

    # Deploy new Armor and Safe contracts.
    armor_address, safe_address = deploy_new_armor(ew3, wallet, safe_owners)

    print()
    print("/*** verifying safe ***\\")
    safe = ISafe(ew3, ew3.to_checksum_address(safe_address))

    is_module_enabled = safe.is_module_enabled(ew3.to_checksum_address(armor_address))
    assert is_module_enabled
    print("==> armor module is enabled")

    read_owners = safe.get_owners()
    print(f"==> safe owners: {read_owners}")

    read_threshold = safe.get_threshold()
    print(f"==> safe threshold: {read_threshold}")

    # Run two transactions to demonstrate the application of the DeFiArmor policy. The first transaction will succeed
    # while the second transaction will fail.
    print()
    print("/*** running transactions ***\\")
    print(
        f"==> transferring WETH from {wallet.address} (wallet) to {owner1.address} (good address)"
    )

    ew3.v0.start_atomic_transaction(wallet.address, safe_address)
    weth: EulithWETH = ew3.v0.get_erc_token(TokenSymbol.WETH)

    # Transferring WETH to a whitelisted address should succeed.
    weth_transfer_tx_params = weth.transfer_float(
        owner1.address, WETH_AMOUNT / 100, {"from": wallet.address, "gas": 100000}
    )
    ew3.eth.send_transaction(weth_transfer_tx_params)

    tx_params = ew3.v0.commit_atomic_transaction()
    tx_params["from"] = wallet.address
    tx_params["gas"] = 200000
    tx = ew3.eth.send_transaction(tx_params)
    receipt = ew3.eth.wait_for_transaction_receipt(tx)

    print(
        f"==> got transaction receipt for good transaction ({receipt['transactionHash'].hex()})"
    )

    bad_address = "0xb16f6CD681917559C032d43E60589aD8b4E26bfF"
    print(
        f"==> sending ETH from {wallet.address} (wallet) to {bad_address} (bad address)"
    )

    ew3.v0.start_atomic_transaction(wallet.address)
    # Transferring WETH to a bad address should not be allowed.
    weth_transfer2_tx_params = weth.transfer_float(
        bad_address, WETH_AMOUNT / 100, {"from": wallet.address, "gas": 100000}
    )
    ew3.eth.send_transaction(weth_transfer2_tx_params)

    error_response = ew3.v0.commit_atomic_transaction()
    assert "message" in error_response
    print(f"==> got error response: {error_response['message']}")
    print()
    print(error_response)


def deploy_new_armor(ew3, wallet, safe_owners):
    print()
    print("/*** deploying armor contract ***\\")
    armor_address, safe_address = ew3.v0.deploy_new_armor(
        ew3.to_checksum_address(wallet.address),
        {
            "from": wallet.address,
            "gas": 2500000,
        },
    )

    print(f"==> armor address: {armor_address}")
    print(f"==> safe address:  {safe_address}")

    owner_addresses = []
    count = 0
    threshold = 2

    print()
    print("/*** enabling armor on safe ***\\")
    for safe_owner in safe_owners:
        owner_addresses.append(safe_owner.address)
        if count < threshold:
            print(f"==> submitting module signature for {safe_owner.address}")
            status = ew3.v0.submit_enable_module_signature(wallet.address, safe_owner)
            assert status
        count += 1

    print(f"==> setting threshold to {threshold}")
    print(f"==> setting owners to {', '.join(owner_addresses)}")
    status = ew3.v0.enable_armor(
        threshold,
        owner_addresses,
        {
            "from": wallet.address,
            "gas": 500000,
        },
    )
    assert status

    return armor_address, safe_address


def get_kms_key(session, key_name: str) -> KmsSigner:
    formatted_key_name = f"alias/{key_name}"
    client = session.client("kms")
    return KmsSigner(client, formatted_key_name)


if __name__ == "__main__":
    print(
        "WARNING: This example requires substantial funds to execute (in the area of 0.3 ETH depending on gas price).\n"
        "\n"
        "It also requires the following keys to be set up in AWS KMS:\n"
        "\n"
        "  * ARMOR_AUTH_ADDRESS\n"
        "  * ARMOR_OWNER1\n"
        "  * ARMOR_OWNER2\n"
        "  * ARMOR_OWNER3\n"
        "\n"
        "ARMOR_AUTH_ADDRESS should be supplied with the ETH and a small amount of WETH.\n"
    )
    input("Press ENTER to continue or Ctrl+C to abort\n")

    print()
    yesno = input(
        "Are you SURE you want to continue and potentially spend 0.3+ ETH (enter 'yes')? "
    )
    if yesno.strip().lower() != "yes":
        print("Aborting!")
        sys.exit(1)

    defi_armor()
