import os
import sys
import time
from typing import Dict

from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.websocket import EulithWebsocketRequestHandler

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner
from utils.settings import EULITH_TOKEN


class MyCustomStreamHandler(EulithWebsocketRequestHandler):
    def __init__(self, ew3: EulithWeb3):
        self.ew3 = ew3

    def handle_result(self, message: Dict):
        result = message.get('params', {}).get('result', {})
        tx_from = result.get('from')
        tx_to = result.get('to')
        tx_data = result.get('input')
        tx_value = result.get('value')

        print(f'##### Pending Tx ######')
        print(f'from: {tx_from}')
        print(f'to: {tx_to}')
        print(f'data: {tx_data}')
        print(f'value: {tx_value}\n')


    def handle_error(self, message: Dict):
        print(f'received an error {message}')


if __name__ == '__main__':
    print_banner()

    with EulithWeb3('https://poly-main.eulithrpc.com/v0', EULITH_TOKEN) as ew3:
        pending_tx_handler = MyCustomStreamHandler(ew3)

        ew3.v0.subscribe_pending_transactions(pending_tx_handler)

        while True:
            time.sleep(1)
