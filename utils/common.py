from eulith_web3.eulith_web3 import EulithWeb3


def check_wallet_balance(ew3: EulithWeb3, min_balance: float):
    if ew3.eth.get_balance(ew3.wallet_address) / 10 ** 18 < min_balance:
        print("Your wallet doesn't have enough balance to complete this example")
        print(f"Please deposit at least {min_balance} ETH")
        exit(1)
