from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IBooster:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [], 'name': 'owner', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_pid', 'type': 'uint256'}], 'name': 'poolInfo', 'outputs': [{'internalType': 'address', 'name': '_lptoken', 'type': 'address'}, {'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'address', 'name': '_gauge', 'type': 'address'}, {'internalType': 'address', 'name': '_crvRewards', 'type': 'address'}, {'internalType': 'address', 'name': '_stash', 'type': 'address'}, {'internalType': 'bool', 'name': '_shutdown', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_voteDelegate', 'type': 'address'}], 'name': 'setVoteDelegate', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_voteId', 'type': 'uint256'}, {'internalType': 'address', 'name': '_votingAddress', 'type': 'address'}, {'internalType': 'bool', 'name': '_support', 'type': 'bool'}], 'name': 'vote', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address[]', 'name': '_gauge', 'type': 'address[]'}, {'internalType': 'uint256[]', 'name': '_weight', 'type': 'uint256[]'}], 'name': 'voteGaugeWeight', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def owner(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.owner().call()

    def pool_info(self, _pid: int) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.poolInfo(_pid).build_transaction()

    def set_vote_delegate(self, _vote_delegate: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setVoteDelegate(_vote_delegate).build_transaction(override_tx_parameters)

    def vote(self, _vote_id: int, _voting_address: str, _support: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.vote(_vote_id, _voting_address, _support).build_transaction(override_tx_parameters)

    def vote_gauge_weight(self, _gauge: List[str], _weight: List[int], override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.voteGaugeWeight(_gauge, _weight).build_transaction(override_tx_parameters)
