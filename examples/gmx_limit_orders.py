from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.gmx import GMXClient
from eulith_web3.signing import LocalSigner, construct_signing_middleware

from utils.banner import print_banner
from utils.settings import PRIVATE_KEY, EULITH_REFRESH_TOKEN

if __name__ == '__main__':
    print_banner()

    print('THIS EXAMPLE DOESNT RUN OUT OF THE BOX. '
          'IT NEEDS AT LEAST $10 WORTH OF WETH AND WE DONT WANT TO PROCURE THAT FOR YOUR IN A BURNER WALLET')
    exit(0)

    # Don't use this in production. Use KMSSigner() instead. You can test with this or with LedgerSigner()
    wallet = LocalSigner(PRIVATE_KEY)
    ew3 = EulithWeb3("https://arb-main.eulithrpc.com/v0", EULITH_REFRESH_TOKEN, construct_signing_middleware(wallet))

    gc = GMXClient(ew3)

    weth = ew3.v0.get_erc_token(TokenSymbol.WETH)

    # You can query for your existing positions easily
    # Note that the lists in this method are linked respectively. In other words, if you pass:
    # [weth, wbtc], [weth, wbtc], [True, False]
    # You're asking for (WETH/WETH/LONG), (WETH/WBTC/SHORT) positions
    positions = gc.get_positions(ew3.to_checksum_address(wallet.address), [weth], [weth], [True])

    if len(positions) > 0:
        # Here are some of the fields available on these position objects
        # There are many others. Have a look at the class underlying to see all available fields
        exposure = positions[0].position_size_denom_usd
        collateral = positions[0].collateral_size_denom_usd

    # Creates a buy limit order
    # (position_token, pay_token, true_for_long, amount_in, size_delta_usd, limit_price_usd, approve_erc)
    # Creates a buy order for $5k USD worth of ETH, paying 1 ETH at $1,500 limit price
    buy_limit_order = gc.create_increase_order(weth, weth, True, 1.0, 5000, 1500, True)
    print(ih.get('transactionHash').hex())

    # Creates a sell limit order
    # (position_token, collateral_token, size_delta_usd, collateral_delta_usd, true_for_long, limit_price_usd)
    # Creates a sell order for $5k USD worth of ETH, unwinding $2k USD worth of collateral at $2,000 limit price
    h = gc.create_decrease_order(weth, weth, 5000, 2000, True, 2000)
    print(h.get('transactionHash').hex())

    #  NOTE: The frontend won't let you submit both of these orders at the same time, but the contracts
    #  don't mind. In other words, you can have a sell limit order pending at the same time as a buy limit order
    #  of course, the sell won't execute unless the buy executes.
