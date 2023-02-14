from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

import config

if __name__ == '__main__':
    
    wallet = config.wallet
    ew3 = config.ew3

    toolkit_contract_address = ew3.eulith_contract_address(wallet.address)
    print("Proxy wallet address is: {}".format(proxy_contract_address))

    token_to_withdraw = ew3.eulith_get_erc_token(TokenSymbol.USDC)

    token_toolkit_balance = token_to_withdraw.balance_of(proxy_contract_address)
    token_toolkit_balance = token_toolkit_balance / token_to_withdraw.decimals
    print("\nBalance is {}".format(token_toolkit_balance))

    # withdraw the whole balance
    amount_to_withdraw = 10

    tx = weth.approve(wallet.address, int(amount_to_withdraw * token_to_withdraw.decimals))
    rec = ew3.eth.send_transaction(tx)
    receipt = ew3.eth.wait_for_transaction_receipt(rec)
    print(f"res 1: {receipt['transactionHash'].hex()}")

    # NOTICE: below is NOT transfer_from because proxy is msg.sender
    tx = weth.transfer(wallet.address, int(amount_to_withdraw * token_to_withdraw.decimals)) 
    rec = ew3.eth.send_transaction(tx)
    receipt = ew3.eth.wait_for_transaction_receipt(rec)
    print(f"res 1: {receipt['transactionHash'].hex()}")