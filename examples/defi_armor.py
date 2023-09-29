import os
import sys

import boto3
from eth_typing import ChecksumAddress
from eulith_web3.exceptions import EulithRpcException

from eulith_web3.erc20 import EulithERC20, TokenSymbol, EulithWETH
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.kms import KmsSigner
from eulith_web3.signer import Signer
from eulith_web3.signing import LocalSigner, construct_signing_middleware
from eulith_web3.contract_bindings.safe.i_safe import ISafe

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import EULITH_TOKEN

EULITH_URL = "https://poly-main.eulithrpc.com/v0"
AWS_CREDENTIALS_PROFILE_NAME = "default"


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
    with EulithWeb3(eulith_url=EULITH_URL, eulith_token=EULITH_TOKEN,
                    signing_middle_ware=construct_signing_middleware(wallet)) as ew3:

        # Handle the POA chain case with Polygon.
        # See http://web3py.readthedocs.io/en/stable/middleware.html#proof-of-authority
        if 'poly' in EULITH_URL:
            from web3.middleware import geth_poa_middleware
            ew3.middleware_onion.inject(geth_poa_middleware, layer=0)

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

        print()
        print(f"/*** setting up whitelist for {owner1.address} ***\\")
        wl = create_new_whitelist(ew3, ew3.to_checksum_address(wallet.address), [owner1.address], safe_owners)
        print(f'==> whitelist contents: {wl}')

        # Run two transactions to demonstrate the application of the DeFiArmor policy.
        # The first transaction will succeed while the second transaction will fail.
        print()
        print("/*** running transactions ***\\")
        print(f"==> transferring ETH/MATIC from {wallet.address} (wallet) to {owner1.address} (good address)")

        ew3.v0.start_atomic_transaction(wallet.address, safe_address)

        # Transferring ETH/MATIC to a whitelisted address should succeed
        ew3.eth.send_transaction({
            'to': owner1.address,
            'from': wallet.address,
            'value': 100
        })

        tx_params = ew3.v0.commit_atomic_transaction()
        tx_params["from"] = wallet.address

        tx = ew3.eth.send_transaction(increase_gas_price_by_factor(tx_params, 10))

        print(f"==> got transaction hash for good transaction ({tx.hex()})\n")

        bad_address = "0xb16f6CD681917559C032d43E60589aD8b4E26bfF"
        print(f"==> sending ETH/MATIC from {wallet.address} (wallet) to {bad_address} (bad address)")

        ew3.v0.start_atomic_transaction(wallet.address)
        # Transferring ETH/MATIC to a bad address should not be allowed.
        ew3.eth.send_transaction({
            'to': bad_address,
            'from': wallet.address,
            'value': 100
        })

        error_response = ew3.v0.commit_atomic_transaction()
        assert "message" in error_response
        print(f"==> got error response: {error_response['message']}")
        print()
        print(error_response)


def deploy_new_armor(ew3, wallet, safe_owners):
    print()
    print("/*** deploying armor contract ***\\")

    wallet_balance = ew3.eth.get_balance(wallet.address)
    if wallet_balance < (0.3 * 1e18):
        print(f'==> wallet {wallet.address} does not have sufficient funds to proceed. Please fund the wallet.')
        exit(1)

    armor_address, safe_address = ew3.v0.get_armor_and_safe_addresses(ew3.to_checksum_address(wallet.address))
    if not armor_address:
        armor_address, safe_address = ew3.v0.deploy_new_armor(
            ew3.to_checksum_address(wallet.address),
            {
                "from": wallet.address,
                "gas": 5000000,
            },
        )

    print(f"==> armor address: {armor_address}")
    print(f"==> safe address:  {safe_address}")

    owner_addresses = []
    count = 0
    threshold = 2

    safe = ISafe(ew3, ew3.to_checksum_address(safe_address))
    if not safe.is_module_enabled(ew3.to_checksum_address(armor_address)):
        print()
        print("/*** enabling armor on safe ***\\")
        for safe_owner in safe_owners:
            owner_addresses.append(safe_owner.address)
            if count < threshold:
                print(f"==> submitting module signature for {safe_owner.address}")
                try:
                    status = ew3.v0.submit_enable_module_signature(wallet.address, safe_owner)
                    assert status
                except EulithRpcException:
                    continue
            count += 1

        print(f"==> setting threshold to {threshold}")
        print(f"==> setting owners to {', '.join(owner_addresses)}")
        status = ew3.v0.enable_armor(
            wallet.address,
            threshold,
            owner_addresses,
            {
                "from": wallet.address,
                "gas": 5000000,
            },
        )
        assert status

    return armor_address, safe_address


def create_new_whitelist(ew3: EulithWeb3, auth_address: ChecksumAddress, addresses: [str], owners: [Signer]):
    current_wl = ew3.v0.get_current_client_whitelist(auth_address)
    current_wl_addresses = set(current_wl.get('active', {}).get('sorted_addresses', []))

    requested_addresses = set([a.lower() for a in addresses])

    if current_wl_addresses == requested_addresses:
        return current_wl_addresses

    draft_wl = current_wl.get('draft', None)
    if not draft_wl:
        list_id = ew3.v0.create_draft_client_whitelist(auth_address, addresses)
    else:
        list_id = draft_wl.get('list_id', 0)

    for o in owners:
        try:
            status = ew3.v0.submit_draft_client_whitelist_signature(list_id, o)
            assert status
        except EulithRpcException:
            continue

    return ew3.v0.get_current_client_whitelist(auth_address).get('active', {}).get('sorted_addresses', [])


def increase_gas_price_by_factor(data, factor):
    gas_keys = ['maxPriorityFeePerGas', 'maxFeePerGas']

    for key in gas_keys:
        int_value = int(data[key], 16)
        doubled_value = int_value * factor
        data[key] = hex(doubled_value)

    return data


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
