from typing import List

import web3.exceptions

from eulith_web3.erc20 import EulithERC20, TokenSymbol
from eulith_web3.swap import EulithSwapRequest


class CurveUtils:
    def __init__(self, eulith_web3, curve_pool):
        self.w3 = eulith_web3
        self.curve_pool = curve_pool
        self.tokens = self.get_pool_tokens()

    def get_pool_tokens(self) -> List[EulithERC20]:
        tokens = []
        for i in range(0, 4):
            try:
                t = self.curve_pool.coins(i)
                tokens.append(EulithERC20(self.w3, self.w3.toChecksumAddress(t)))
            except web3.exceptions.ContractLogicError:
                break

        return tokens

    def get_lp_token_value_denominated_usd(self) -> float:
        usdc = self.w3.v0.get_erc_token(TokenSymbol.USDC)

        total_usd_value = 0

        for i, coin in enumerate(self.tokens):
            bal = self.curve_pool.balances(i)
            bal_float = bal / 10 ** coin.decimals
            price, txs = self.w3.v0.get_swap_quote(EulithSwapRequest(
                sell_token=usdc,
                buy_token=coin,
                sell_amount=1
            ))
            dollar_denominated_balance = bal_float * price
            total_usd_value += dollar_denominated_balance

        lp_token = EulithERC20(self.w3, self.w3.toChecksumAddress(self.curve_pool.token()))
        lp_supply = lp_token.total_supply() / 10 ** lp_token.decimals

        return total_usd_value / lp_supply
