from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

import boto3
from eulith_web3.kms import KmsSigner

from eulith_web3.eulith_web3 import *
from eulith_web3.signing import construct_signing_middleware

import config
import master_trading_code as mtc

if __name__ == '__main__':
	print("Starting swap...")
	wallet = config.wallet
	ew3 = config.ew3

	weth = ew3.eulith_get_erc_token(TokenSymbol.WETH)
	usdt = ew3.eulith_get_erc_token(TokenSymbol.USDT)
	usdc = ew3.eulith_get_erc_token(TokenSymbol.USDC)

	amount = 0.001

	swap = EulithSwapRequest(
		sell_token = weth, 
		buy_token = usdc, 
		sell_amount = amount, 
		recipient = wallet.address,
		route_through = EulithSwapProvider.ONE_INCH
		)

	price, txs = ew3.eulith_swap_quote(swap)

	print(f"Price is: {1/price}")

	mtc.fund_toolkit_contract_if_needed(amount, weth, 1e18)

	# could check price, will just execute small amount
	ew3.eulith_start_transaction(wallet.address)
	ew3.eulith_send_multi_transaction(txs)
	final_tx = ew3.eulith_commit_transaction()
	rec = ew3.eth.send_transaction(final_tx)

	print(f"\nReceipt is:\n {rec.hex()}.")
