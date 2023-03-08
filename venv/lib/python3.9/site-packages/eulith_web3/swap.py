from enum import Enum
from typing import TypedDict, Optional

from eth_typing import ChecksumAddress

from eulith_web3.erc20 import EulithERC20


class EulithSwapProvider(str, Enum):
    ZERO_EX = 'zero_ex'
    ONE_INCH = "one_inch"


class EulithLiquiditySource(str, Enum):
    UNISWAP_V1 = 'uniswap_v1'
    UNISWAP_V2 = 'uniswap_v2'
    UNISWAP_V3 = 'uniswap_v3'
    BALANCER_V1 = 'balancer_v1'
    BALANCER_V2 = 'balancer_v2'
    CURVE_V1 = 'curve_v1'
    CURVE_V2 = 'curve_v2'
    COMPOUND = 'compound'
    PANCAKE = 'pancake'
    AAVE_V1 = 'aave_v1'
    AAVE_V2 = 'aave_v2'
    DODO_V1 = 'dodo_v1'
    DODO_V2 = 'dodo_v2'
    SUSHI = 'sushi'
    KYBER = 'kyber'
    BANCOR_V1 = 'bancor_v1'
    BANCOR_V3 = 'bancor_v3'
    LIDO = 'lido'
    MAKER_PSM = 'maker_psm'
    MSTABLE = 'mstable'
    SADDLE = 'saddle'
    SHELL = 'shell'
    SHIBA = 'shiba'
    SYNAPSE = 'synapse'
    SYNTHETIX = 'synthetix'


class EulithSwapRequest(TypedDict):
    sell_token: EulithERC20
    buy_token: EulithERC20
    sell_amount: float
    recipient: Optional[ChecksumAddress]
    route_through: Optional[EulithSwapProvider]
    slippage_tolerance: Optional[float]
    liquidity_source: Optional[EulithLiquiditySource]

