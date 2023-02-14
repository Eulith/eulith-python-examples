from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

if __name__ == '__main__':
    
    wallet = LocalSigner("...") 
    ew3 = EulithWeb3(eulith_url="https://eth-main.eulithrpc.com/v0",
                     eulith_refresh_token="...", # YOUR REFRESH TOKEN GOES HERE
                     signing_middle_ware=construct_signing_middleware(wallet)
                     )

    proxy_contract_address = ew3.eulith_contract_address(wallet.address)
    print("Proxy wallet address is: {}".format(proxy_contract_address))

    weth = ew3.eulith_get_erc_token(TokenSymbol.WETH)

    weth_proxy_balance = weth.balance_of(proxy_contract_address)
    weth_proxy_balance = weth_proxy_balance / 1e18
    print("\nBalance is {}".format(weth_proxy_balance))

    ew3.eulith_start_transaction(wallet.address)

    tx = weth.approve(wallet.address, int(1e20))
    res = ew3.eth.send_transaction(tx)
    print("res 1: {}".format(res.hex()))

    # NOTICE: below is NOT transfer_from because proxy is msg.sender
    tx = weth.transfer(wallet.address, int(weth_proxy_balance*1e18)) 
    res = ew3.eth.send_transaction(tx)
    print("\nres 2: {}".format(res.hex()))

    tx = ew3.eulith_commit_transaction()

    # !! Setting gas cost parameters as a constants for now, should improve later !!
    gas_max_priority_fee = 5000000000 # 5 Gwei, minner tip (in addition to base price)
    gas_usage = 750000 # 75,000 gas
    
    # set your gas limit, right now this has to be done entirely by the client
    tx['maxPriorityFeePerGas'] = gas_max_priority_fee
    tx['gas'] = gas_usage

    # send the transaction!
    tx = ew3.eth.send_transaction(tx)
    print("Transaction is: {}".format(tx.hex()))

    receipt = ew3.eth.wait_for_transaction_receipt(tx)
    print(receipt)