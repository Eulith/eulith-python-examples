from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware, LocalSigner

# ------ Eulith from here on ----- #
wallet = LocalSigner("...") # YOUR PRIVATE KEY GOES HERE
network_url = "https://eth-main.eulithrpc.com/v0"
ew3 = EulithWeb3(eulith_url=network_url,
                 eulith_refresh_token="...", # YOUR REFRESH TOKEN GOES HERE
                 signing_middle_ware=construct_signing_middleware(wallet)
                 )

proxy_contract_address = ew3.eulith_contract_address(wallet.address)
print("Proxy wallet address is: {}".format(proxy_contract_address))

weth = ew3.eulith_get_erc_token(TokenSymbol.WETH)
weth_proxy_balance = weth.balance_of(proxy_contract_address)
weth_proxy_balance = weth_proxy_balance / 1e18

print("\nBalance is {}".format(weth_proxy_balance))

print("Address is: {}".format(weth.address))
