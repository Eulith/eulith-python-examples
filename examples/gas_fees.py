import os
import sys

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

sys.path.insert(0, os.getcwd())
from utils.settings import PRIVATE_KEY, EULITH_REFRESH_TOKEN
from utils.banner import print_banner


"""
Gas is the unit of measurement for the computational effort required to execute a transaction or contract on the 
Ethereum blockchain. Every operation in a smart contract requires a certain amount of gas, as it is the cost of 
computational resources for processing the logic within a transaction. Depending on ethereum blockchain traffic and 
network congestion, baseFeePerGas can fluctuate.
"""

if __name__ == '__main__':
    print_banner()

    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://eth-main.eulithrpc.com/v0", EULITH_REFRESH_TOKEN, construct_signing_middleware(wallet))

    # Can be used to convert from wei to gwei, or gwei to eth. Relation: 1 eth = 1e9 gwei = 1e18 wei
    MIDDLE_UNIT_CONVERSION = 1e9
    WEI_ETH_CONVERSION = 1e18
    BLOCK_RANGE = 10

    GAS_FEE_MODES = {
        "slow": [10, 20, 30, 40, 50],
        "normal": [0, 30, 50, 70, 100],
        "fast": [50, 60, 70, 80, 90]
    }
    speed = 'normal'  # default speed is set to normal, this is customizable

    # Gas units are set based on past transaction spending averages for each type of transaction
    transaction_gas_usage = {
        "atomic_swap": 250000,
        "deposit": 28000,
        "token_transfer": 21000,
        "contract_deposit": 40000,
        "contract_withdrawal": 35000,
        "toolkit_funding": 115000,
        "contract_deployment": 500000
    }
    transaction_type = "token_transfer"

    # Transaction gas limit is set to 2 times the estimated gas usage, as gas usage typically doesn't exceed it.
    # Unused gas from a function is returned, however note that ant to maximize the number of transactions they can
    # include in a block while also earning as much in transaction fees as possible so setting high gas limits may cause
    # transactions to get stuck in the mempool
    transaction_gas_limits = {transaction_type: gas_usage * 2 for transaction_type, gas_usage in
                              transaction_gas_usage.items()}

    if speed not in GAS_FEE_MODES:
        raise ValueError("Speed values can be set to slow, normal, or fast")

    pending_block_base_fee = (ew3.eth.get_block('pending').baseFeePerGas) / MIDDLE_UNIT_CONVERSION

    # For transactions to be included in a block, gas price must be at least equal to base fee reserve price, otherwise
    # increasing by a maximum of 12.5% per block if the target block size is exceeded. next_block_max_base_fee is set
    # to 125% of pending_block_base_fee to account for worst case scenario of high congestion
    next_block_max_base_fee = pending_block_base_fee * 1.25
    print(f"To include transactions, current pending block base fee per gas required to include transactions: {pending_block_base_fee:.2f} gwei."
          f" Next block max base fee: {next_block_max_base_fee:.2f} gwei")

    next_block_gas_price = ew3.eth.gas_price / MIDDLE_UNIT_CONVERSION
    print(f"Gas price to include transactions in the next block is {next_block_gas_price:.2f} gwei")

    fee_history = ew3.eth.fee_history(BLOCK_RANGE, 'pending', GAS_FEE_MODES[speed])
    current_reward_history_flat = sum(fee_history['reward'], [])
    average_miner_reward = sum(current_reward_history_flat) // len(current_reward_history_flat)
    print(f"Average miner reward is {(average_miner_reward / MIDDLE_UNIT_CONVERSION):.2f} gwei")

    # Average priority fee could be negative if the next block gas price is lower than the pending block base fee.
    # Note that If the total fee (base fee + priority fee) you offer for a transaction exceeds
    # the maximum fee limit, the priority fee will be automatically reduced to fit within the limit. This means that
    # the actual tip (priority fee) may be smaller than the one you specified, and under such circumstances, your
    # transaction may become less attractive to miners for inclusion in the next block. Depending on frequency needs,
    # find a balance between setting a reasonable fee and ensuring your transaction is confirmed quickly.
    priority_fee = abs(next_block_gas_price - pending_block_base_fee)
    print(f"Recommended max priority fee tip to miners: {priority_fee:.2f}")

    gas_usage = transaction_gas_usage[transaction_type] * (pending_block_base_fee + priority_fee)
    gas_usage_limit = transaction_gas_limits[transaction_type] * (pending_block_base_fee + priority_fee)
    print(f"For a {transaction_type} transaction, the gas usage is an estimated {(gas_usage / MIDDLE_UNIT_CONVERSION):.6f} eth "
          f"and gas limit should be set to {(gas_usage_limit / MIDDLE_UNIT_CONVERSION):.6f} eth")


