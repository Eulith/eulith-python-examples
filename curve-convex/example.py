import boto3

from eulith_web3.contract_bindings.curve.curve_v2_tri_crypto import CurveV2TriCrypto
from eulith_web3.contract_bindings.convex.i_convex_deposits import IConvexDeposits
from eulith_web3.contract_bindings.convex.i_reward_staking import IRewardStaking
from eulith_web3.curve import EulithCommonCurvePool
from eulith_web3.erc20 import EulithERC20, TokenSymbol, EulithWETH
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.kms import KmsSigner
from eulith_web3.signing import construct_signing_middleware
from eulith_web3.swap import EulithSwapRequest

TRI_CRYPTO_POOL_ADDRESS = '0xd51a44d3fae010294c616388b506acda1bfaae46'
CONVEX_BOOSTER_ADDRESS = '0xf403c135812408bfbe8713b5a23a04b3d48aae31'
CONVEX_REWARD_ADDRESS = '0x9D5C5E364D81DaB193b72db9E9BE9D8ee669B652'

if __name__ == '__main__':
    aws_credentials_profile_name = '<YOUR_CREDENTIALS_PROFILE>'
    key_name = '<YOUR_KEY_NAME>'
    formatted_key_name = f'alias/{key_name}'

    session = boto3.Session(profile_name=aws_credentials_profile_name, region_name='<YOUR_REGION>')
    client = session.client('kms')
    wallet = KmsSigner(client, formatted_key_name)

    print(f'Wallet Address: {wallet.address}\n')

    ew3 = EulithWeb3(eulith_url='https://eth-main.eulithrpc.com/v0',
                     eulith_refresh_token='<YOUR_REFRESH_TOKEN>',
                     signing_middle_ware=construct_signing_middleware(wallet))

    usdc = ew3.v0.get_erc_token(TokenSymbol.USDC)

    # Curve pool contracts are very poorly abstracted, but we take some liberties to abstract basic logic here
    common_pool = EulithCommonCurvePool(ew3, ew3.toChecksumAddress(TRI_CRYPTO_POOL_ADDRESS))
    tokens = common_pool.get_pool_tokens()

    token_string = 'Pool Tokens:'
    for i, token in enumerate(tokens):
        token_string += f"  |  Token {i}: {token.symbol}"

    print(token_string)

    # To do anything useful, you have to instantiate the specific pool you're wanting to interact with
    tri_pool = CurveV2TriCrypto(ew3, ew3.toChecksumAddress(TRI_CRYPTO_POOL_ADDRESS))

    lp_token = EulithERC20(ew3, ew3.toChecksumAddress(tri_pool.token()))

    deposit_token = EulithWETH(ew3, tokens[2].address)  # for this particular pool, third token is WETH
    deposit_amount = 0.02
    deposit_amount_wei = deposit_amount * 10 ** deposit_token.decimals

    # [USDT, WBTC, WETH]
    deposit_list = [0, 0, int(deposit_amount_wei)]

    expected_lp_amount = tri_pool.calc_token_amount(deposit_list, False)  # False = use WETH, don't need to convert from ETH
    expected_lp_amount_float = expected_lp_amount / 10 ** lp_token.decimals

    # Get the price of our deposit token, denominated in USD, so we can calculate our dollar denominated
    # values below
    price, txs = ew3.v0.get_swap_quote(EulithSwapRequest(
        sell_token=usdc,
        buy_token=deposit_token,
        sell_amount=1
    ))

    lp_token_value = common_pool.get_lp_token_value_denominated_usd()

    dollar_denominated_input = deposit_amount * price
    dollar_denominated_lp_output = expected_lp_amount_float * lp_token_value

    print(f'Dollar denominated value IN (deposit): ${round(dollar_denominated_input, 3)}, '
          f'OUT (lp token): ${round(dollar_denominated_lp_output, 3)}')

    # ---------- EXECUTE DEPOSIT -------------- #

    deposit_token_balance = deposit_token.balance_of_float(wallet.address)
    if deposit_token_balance < deposit_amount:
        to_deposit = deposit_amount - deposit_token_balance
        deposit_tx = deposit_token.deposit_eth(to_deposit, {'from': wallet.address, 'gas': 100000})
        ew3.eth.send_transaction(deposit_tx)

    pool_allowance = deposit_token.allowance_float(
        ew3.toChecksumAddress(wallet.address),
        ew3.toChecksumAddress(TRI_CRYPTO_POOL_ADDRESS))
    if pool_allowance < deposit_amount:
        approve_tx = deposit_token.approve_float(ew3.toChecksumAddress(TRI_CRYPTO_POOL_ADDRESS),
                                                 deposit_amount, {'from': wallet.address, 'gas': 100000})
        ew3.eth.send_transaction(approve_tx)

    deposit_to_curve = False  # set false to switch off the below Curve deposit
    if deposit_to_curve:
        # Example: https://etherscan.io/tx/0x7e91a8e7a0bb2d9e1c54f282ba1a54e31653cfaa1b24e2478353f298a117e497
        tx = tri_pool.add_liquidity(deposit_list, expected_lp_amount, {'from': wallet.address, 'gas': 400000})
        tx_hash = ew3.eth.send_transaction(tx).hex()
        print(f'Curve pool deposit tx hash: {tx_hash}')

    current_lp_token_balance = lp_token.balance_of(wallet.address)
    print(f'\nCurrent Curve LP token balance: {current_lp_token_balance / 10**lp_token.decimals} | LP Token address: {lp_token.address}')

    deposit_to_convex = False  # set false to switch off the below Convex deposit
    if current_lp_token_balance > 0 and deposit_to_convex:
        convex_allowance = lp_token.allowance(wallet.address, ew3.toChecksumAddress(CONVEX_BOOSTER_ADDRESS))
        if convex_allowance < current_lp_token_balance:
            to_allow = current_lp_token_balance - convex_allowance
            approve_tx = lp_token.approve(ew3.toChecksumAddress(CONVEX_BOOSTER_ADDRESS),
                                          current_lp_token_balance, {'from': wallet.address, 'gas': 100000})
            approve_hash = ew3.eth.send_transaction(approve_tx)
            ew3.eth.wait_for_transaction_receipt(approve_hash)

        convex_contract = IConvexDeposits(ew3, ew3.toChecksumAddress(CONVEX_BOOSTER_ADDRESS))
        # 38 is the magic number for TriPool that comes from https://www.convexfinance.com/stake
        # True here is to enable stake (to start earning rewards)
        cvx_tx = convex_contract.deposit(38, current_lp_token_balance, True, {'from': wallet.address, 'gas': 800000})
        cvx_hash = ew3.eth.send_transaction(cvx_tx).hex()
        print(f'Convex deposit tx hash: {cvx_hash}')

    convex_staking_contract = IRewardStaking(ew3, ew3.toChecksumAddress(CONVEX_REWARD_ADDRESS))
    staked_balance = convex_staking_contract.balance_of(wallet.address)
    print(f'\nConvex staked balance: {staked_balance} | LP Token address: {lp_token.address}')
    current_rewards = convex_staking_contract.earned(wallet.address)
    print(f'Convex earned rewards: {current_rewards} CRV')

    claim_reward = False  # set false to switch off the below Convex reward claim
    if claim_reward:
        claim_tx = convex_staking_contract.get_reward({'from': wallet.address, 'gas': 200000})
        claim_hash = ew3.eth.send_transaction(claim_tx).hex()
        print(f'Convex claim tx hash: {claim_hash}')

    crv = ew3.v0.get_erc_token(TokenSymbol.CRV)
    crv_bal = crv.balance_of_float(wallet.address)
    print(f'CRV (reward token) balance: {crv_bal}')

