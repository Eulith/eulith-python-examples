from functools import reduce
import os
import sys

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

sys.path.insert(0, os.getcwd())
from utils.settings import PRIVATE_KEY, EULITH_REFRESH_TOKEN
from utils.banner import print_banner


if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_REFRESH_TOKEN, construct_signing_middleware(wallet))

    toolkit_contract_address = ew3.v0.ensure_toolkit_contract(wallet.address)

    SELL_TOKEN = ew3.v0.get_erc_token(TokenSymbol.USDC)
    BUY_TOKEN = ew3.v0.get_erc_token(TokenSymbol.WETH)

    aggregator = EulithSwapProvider.ZERO_EX
    gas_limit = 100000
    gas_price = (ew3.eth.gas_price / 1e9) * gas_limit / 1e9
    if aggregator == EulithSwapProvider.ZERO_EX:
        gas_usage = 800000
    elif aggregator == EulithSwapProvider.ONE_INCH:
        gas_usage = 450000

    GAS_FEE_MODES = {
        "slow": [10, 20, 30, 40, 50],
        "normal": [10, 30, 50, 70, 90],
        "fast": [50, 60, 70, 80, 90],
    }

    speed = 'normal'
    block_range = 10
    if speed not in GAS_FEE_MODES:
        raise ValueError("Speed values can be set to slow, normal, or fast")

    base_fee = ew3.eth.get_block('pending').baseFeePerGas
    estimated_next_base_fee = base_fee * 2
    current_reward_history = ew3.eth.fee_history(block_range, 'pending', GAS_FEE_MODES[speed])['reward']
    rewards = reduce(lambda x, y: x + y, current_reward_history)
    average_reward = sum(rewards) // len(rewards)
    max_priority_fee = average_reward
    max_fee = average_reward + estimated_next_base_fee

    print(f"Average gas fee for transactions with gas limit set to {gas_limit} is {gas_price:.5f} eth")
    print(f"The estimated live maxPriorityFeePerGas is {max_priority_fee / 1e9:.5f} gwei and live maxFeePerGas is "
          f"{max_fee / 1e9:.5f} gwei")

    GWEI_AND_ETH_CONVERSION = 1e18
    max_gas_price = 35000000000 # wei
    max_gas_price = max_gas_price / GWEI_AND_ETH_CONVERSION # do this first to avoid multiplying large numbers
    gas_cost_in_eth = max_gas_price * gas_usage
    max_gas_price = max_gas_price * GWEI_AND_ETH_CONVERSION

    if SELL_TOKEN.address != "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2":
        print(f"\nSell_token is {SELL_TOKEN.symbol}")
        swap_params = EulithSwapRequest(
            sell_token=SELL_TOKEN,
            buy_token=BUY_TOKEN,
            sell_amount=1.0)

        try:
            sell_token_to_eth_price, txs = ew3.v0.get_swap_quote(swap_params)
        except EulithRpcException as e:
            print(e)
        gas_cost_in_sell_token = gas_cost_in_eth * GWEI_AND_ETH_CONVERSION

    else:
        gas_cost_in_sell_token = gas_cost_in_eth

    print(f"Estimated gas cost in {SELL_TOKEN.symbol} is {gas_cost_in_sell_token/1e18} eth")
    print(f"The current block's baseFeePerGas is {base_fee / 1e9:.5f} gwei")
    print(f"The estimated next block's baseFeePerGas is {estimated_next_base_fee / 1e9:.5f} gwei")
    print(f"The reward history for the past {block_range} blocks with {speed} speed is: {current_reward_history}")
    print(f"The average reward for the past {block_range} blocks with {speed} speed is: {average_reward / 1e9:.5f} gwei. This confirms the max priority fee of {max_priority_fee / 1e9} gwei")