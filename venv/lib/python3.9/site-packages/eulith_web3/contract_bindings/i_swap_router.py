from typing import Optional, Union
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class ISwapRouter:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'components': [{'internalType': 'bytes', 'name': 'path', 'type': 'bytes'}, {'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'uint256', 'name': 'deadline', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amountIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amountOutMinimum', 'type': 'uint256'}], 'internalType': 'struct ISwapRouter.ExactInputParams', 'name': 'params', 'type': 'tuple'}], 'name': 'exactInput', 'outputs': [{'internalType': 'uint256', 'name': 'amountOut', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'components': [{'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'internalType': 'uint24', 'name': 'fee', 'type': 'uint24'}, {'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'uint256', 'name': 'deadline', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amountIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amountOutMinimum', 'type': 'uint256'}, {'internalType': 'uint160', 'name': 'sqrtPriceLimitX96', 'type': 'uint160'}], 'internalType': 'struct ISwapRouter.ExactInputSingleParams', 'name': 'params', 'type': 'tuple'}], 'name': 'exactInputSingle', 'outputs': [{'internalType': 'uint256', 'name': 'amountOut', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'components': [{'internalType': 'bytes', 'name': 'path', 'type': 'bytes'}, {'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'uint256', 'name': 'deadline', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amountOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amountInMaximum', 'type': 'uint256'}], 'internalType': 'struct ISwapRouter.ExactOutputParams', 'name': 'params', 'type': 'tuple'}], 'name': 'exactOutput', 'outputs': [{'internalType': 'uint256', 'name': 'amountIn', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'components': [{'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'internalType': 'uint24', 'name': 'fee', 'type': 'uint24'}, {'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'uint256', 'name': 'deadline', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amountOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amountInMaximum', 'type': 'uint256'}, {'internalType': 'uint160', 'name': 'sqrtPriceLimitX96', 'type': 'uint160'}], 'internalType': 'struct ISwapRouter.ExactOutputSingleParams', 'name': 'params', 'type': 'tuple'}], 'name': 'exactOutputSingle', 'outputs': [{'internalType': 'uint256', 'name': 'amountIn', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'int256', 'name': 'amount0Delta', 'type': 'int256'}, {'internalType': 'int256', 'name': 'amount1Delta', 'type': 'int256'}, {'internalType': 'bytes', 'name': 'data', 'type': 'bytes'}], 'name': 'uniswapV3SwapCallback', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def exact_input(self, params: tuple, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.exactInput(params).build_transaction(override_tx_parameters)

    def exact_input_single(self, params: tuple, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.exactInputSingle(params).build_transaction(override_tx_parameters)

    def exact_output(self, params: tuple, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.exactOutput(params).build_transaction(override_tx_parameters)

    def exact_output_single(self, params: tuple, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.exactOutputSingle(params).build_transaction(override_tx_parameters)

    def uniswap_v3_swap_callback(self, amount0_delta: None, amount1_delta: None, data: bytes, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.uniswapV3SwapCallback(amount0_delta, amount1_delta, data).build_transaction(override_tx_parameters)
