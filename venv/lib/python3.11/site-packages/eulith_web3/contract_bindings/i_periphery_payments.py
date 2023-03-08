from typing import Optional, Union
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IPeripheryPayments:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [], 'name': 'refundETH', 'outputs': [], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'token', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amountMinimum', 'type': 'uint256'}, {'internalType': 'address', 'name': 'recipient', 'type': 'address'}], 'name': 'sweepToken', 'outputs': [], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': 'amountMinimum', 'type': 'uint256'}, {'internalType': 'address', 'name': 'recipient', 'type': 'address'}], 'name': 'unwrapWETH9', 'outputs': [], 'stateMutability': 'payable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def refund_e_t_h(self, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.refundETH().build_transaction(override_tx_parameters)

    def sweep_token(self, token: str, amount_minimum: int, recipient: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.sweepToken(token, amount_minimum, recipient).build_transaction(override_tx_parameters)

    def unwrap_w_e_t_h9(self, amount_minimum: int, recipient: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.unwrapWETH9(amount_minimum, recipient).build_transaction(override_tx_parameters)
