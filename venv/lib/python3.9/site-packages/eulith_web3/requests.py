from typing import TypedDict, Optional, List

from eth_typing import ChecksumAddress

from eulith_web3.erc20 import EulithERC20


# ~~~~~~~~~~~~ SHORT ~~~~~~~~~~~~~~~~~~~
class EulithShortOnRequest(TypedDict):
    collateral_token: EulithERC20
    short_token: EulithERC20
    collateral_amount: float


class EulithShortOffRequest(TypedDict):
    collateral_token: EulithERC20
    short_token: EulithERC20
    repay_short_amount: float
    true_for_unwind_a: Optional[bool]


# ~~~~~~~~~~~~ AAVE V2 ~~~~~~~~~~~~~~~~~~~
class EulithAaveV2InnerLoanBody(TypedDict):
    token_address: EulithERC20
    amount: float


class EulithAaveV2StartLoanRequest(TypedDict):
    tokens: List[EulithAaveV2InnerLoanBody]


# ~~~~~~~~~~~~ FLASH ~~~~~~~~~~~~~~~~~~~
class FlashRequest(TypedDict):
    take: EulithERC20
    pay: EulithERC20
    take_amount: float
    recipient: Optional[ChecksumAddress]
    pay_transfer_from: Optional[ChecksumAddress]