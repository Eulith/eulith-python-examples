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
	wallet = config.wallet
	ew3 = config.ew3

	send_to = "..."
	amount_in_eth = 0.0001

	print(f"Sending {amount_in_eth} eth to: {send_to}")

	rec = ew3.eth.send_transaction({'from': wallet.address,
                              		'to': send_to, 
                             		'value': hex(int(amount_in_eth * 1e18))})

	receipt = ew3.eth.wait_for_transaction_receipt(rec)

	print(f"Eth sent, txn hash: {receipt['transactionHash'].hex()}")
