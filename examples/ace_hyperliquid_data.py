import os
import sys

from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.hyperliquid.rpc import HyperliquidGetDataRequest, HyperliquidDataType
from eulith_web3.signing import LocalSigner, construct_signing_middleware

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import *

wallet = LocalSigner(PRIVATE_KEY)

with EulithWeb3("https://poly-main.eulithrpc.com/v0", EULITH_TOKEN, construct_signing_middleware(wallet)) as ew3:
    print_banner()

    data_request = HyperliquidGetDataRequest(
        account_address='0xACEE62283c41aEBD7B4E79B2A0031b07b07763f3',  # your Hyperliquid account address
        data_type=HyperliquidDataType.MID_PRICES,
        ace_address=ew3.to_checksum_address('0xfc11e697f23e5cbbed3c59ac249955da57e57672')  # your ACE address
    )

    data = ew3.hyperliquid.get_data(data_request)
    print(data)
