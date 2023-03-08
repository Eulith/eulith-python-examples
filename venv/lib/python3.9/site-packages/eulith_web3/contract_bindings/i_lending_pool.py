from typing import Optional, Union
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class ILendingPool:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'indexed': False, 'internalType': 'address', 'name': 'user', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'onBehalfOf', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'borrowRateMode', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'borrowRate', 'type': 'uint256'}, {'indexed': True, 'internalType': 'uint16', 'name': 'referral', 'type': 'uint16'}], 'name': 'Borrow', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'indexed': False, 'internalType': 'address', 'name': 'user', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'onBehalfOf', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}, {'indexed': True, 'internalType': 'uint16', 'name': 'referral', 'type': 'uint16'}], 'name': 'Deposit', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'target', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'initiator', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'asset', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'premium', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint16', 'name': 'referralCode', 'type': 'uint16'}], 'name': 'FlashLoan', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'collateralAsset', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'debtAsset', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'user', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'debtToCover', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'liquidatedCollateralAmount', 'type': 'uint256'}, {'indexed': False, 'internalType': 'address', 'name': 'liquidator', 'type': 'address'}, {'indexed': False, 'internalType': 'bool', 'name': 'receiveAToken', 'type': 'bool'}], 'name': 'LiquidationCall', 'type': 'event'}, {'anonymous': False, 'inputs': [], 'name': 'Paused', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'RebalanceStableBorrowRate', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'user', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'repayer', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}], 'name': 'Repay', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'liquidityRate', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'stableBorrowRate', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'variableBorrowRate', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'liquidityIndex', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'variableBorrowIndex', 'type': 'uint256'}], 'name': 'ReserveDataUpdated', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'ReserveUsedAsCollateralDisabled', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'ReserveUsedAsCollateralEnabled', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'user', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'rateMode', 'type': 'uint256'}], 'name': 'Swap', 'type': 'event'}, {'anonymous': False, 'inputs': [], 'name': 'Unpaused', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'user', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'to', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}], 'name': 'Withdraw', 'type': 'event'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'interestRateMode', 'type': 'uint256'}, {'internalType': 'uint16', 'name': 'referralCode', 'type': 'uint16'}, {'internalType': 'address', 'name': 'onBehalfOf', 'type': 'address'}], 'name': 'borrow', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}, {'internalType': 'address', 'name': 'onBehalfOf', 'type': 'address'}, {'internalType': 'uint16', 'name': 'referralCode', 'type': 'uint16'}], 'name': 'deposit', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}, {'internalType': 'address', 'name': 'from', 'type': 'address'}, {'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'balanceFromAfter', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'balanceToBefore', 'type': 'uint256'}], 'name': 'finalizeTransfer', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiverAddress', 'type': 'address'}, {'internalType': 'address[]', 'name': 'assets', 'type': 'address[]'}, {'internalType': 'uint256[]', 'name': 'amounts', 'type': 'uint256[]'}, {'internalType': 'uint256[]', 'name': 'modes', 'type': 'uint256[]'}, {'internalType': 'address', 'name': 'onBehalfOf', 'type': 'address'}, {'internalType': 'bytes', 'name': 'params', 'type': 'bytes'}, {'internalType': 'uint16', 'name': 'referralCode', 'type': 'uint16'}], 'name': 'flashLoan', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'getAddressesProvider', 'outputs': [{'internalType': 'contract ILendingPoolAddressesProvider', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}], 'name': 'getConfiguration', 'outputs': [{'components': [{'internalType': 'uint256', 'name': 'data', 'type': 'uint256'}], 'internalType': 'struct DataTypes.ReserveConfigurationMap', 'name': '', 'type': 'tuple'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}], 'name': 'getReserveData', 'outputs': [{'components': [{'components': [{'internalType': 'uint256', 'name': 'data', 'type': 'uint256'}], 'internalType': 'struct DataTypes.ReserveConfigurationMap', 'name': 'configuration', 'type': 'tuple'}, {'internalType': 'uint128', 'name': 'liquidityIndex', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'variableBorrowIndex', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'currentLiquidityRate', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'currentVariableBorrowRate', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'currentStableBorrowRate', 'type': 'uint128'}, {'internalType': 'uint40', 'name': 'lastUpdateTimestamp', 'type': 'uint40'}, {'internalType': 'address', 'name': 'aTokenAddress', 'type': 'address'}, {'internalType': 'address', 'name': 'stableDebtTokenAddress', 'type': 'address'}, {'internalType': 'address', 'name': 'variableDebtTokenAddress', 'type': 'address'}, {'internalType': 'address', 'name': 'interestRateStrategyAddress', 'type': 'address'}, {'internalType': 'uint8', 'name': 'id', 'type': 'uint8'}], 'internalType': 'struct DataTypes.ReserveData', 'name': '', 'type': 'tuple'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}], 'name': 'getReserveNormalizedIncome', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}], 'name': 'getReserveNormalizedVariableDebt', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getReservesList', 'outputs': [{'internalType': 'address[]', 'name': '', 'type': 'address[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'getUserAccountData', 'outputs': [{'internalType': 'uint256', 'name': 'totalCollateralETH', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'totalDebtETH', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'availableBorrowsETH', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'currentLiquidationThreshold', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'ltv', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'healthFactor', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'getUserConfiguration', 'outputs': [{'components': [{'internalType': 'uint256', 'name': 'data', 'type': 'uint256'}], 'internalType': 'struct DataTypes.UserConfigurationMap', 'name': '', 'type': 'tuple'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'internalType': 'address', 'name': 'aTokenAddress', 'type': 'address'}, {'internalType': 'address', 'name': 'stableDebtAddress', 'type': 'address'}, {'internalType': 'address', 'name': 'variableDebtAddress', 'type': 'address'}, {'internalType': 'address', 'name': 'interestRateStrategyAddress', 'type': 'address'}], 'name': 'initReserve', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'collateralAsset', 'type': 'address'}, {'internalType': 'address', 'name': 'debtAsset', 'type': 'address'}, {'internalType': 'address', 'name': 'user', 'type': 'address'}, {'internalType': 'uint256', 'name': 'debtToCover', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'receiveAToken', 'type': 'bool'}], 'name': 'liquidationCall', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'paused', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}, {'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'rebalanceStableBorrowRate', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'rateMode', 'type': 'uint256'}, {'internalType': 'address', 'name': 'onBehalfOf', 'type': 'address'}], 'name': 'repay', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'internalType': 'uint256', 'name': 'configuration', 'type': 'uint256'}], 'name': 'setConfiguration', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': 'val', 'type': 'bool'}], 'name': 'setPause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'reserve', 'type': 'address'}, {'internalType': 'address', 'name': 'rateStrategyAddress', 'type': 'address'}], 'name': 'setReserveInterestRateStrategyAddress', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}, {'internalType': 'bool', 'name': 'useAsCollateral', 'type': 'bool'}], 'name': 'setUserUseReserveAsCollateral', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}, {'internalType': 'uint256', 'name': 'rateMode', 'type': 'uint256'}], 'name': 'swapBorrowRateMode', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'asset', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}, {'internalType': 'address', 'name': 'to', 'type': 'address'}], 'name': 'withdraw', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def borrow(self, asset: str, amount: int, interest_rate_mode: int, referral_code: None, on_behalf_of: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.borrow(asset, amount, interest_rate_mode, referral_code, on_behalf_of).build_transaction(override_tx_parameters)

    def deposit(self, asset: str, amount: int, on_behalf_of: str, referral_code: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.deposit(asset, amount, on_behalf_of, referral_code).build_transaction(override_tx_parameters)

    def finalize_transfer(self, asset: str, _from: str, to: str, amount: int, balance_from_after: int, balance_to_before: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.finalizeTransfer(asset, _from, to, amount, balance_from_after, balance_to_before).build_transaction(override_tx_parameters)

    def flash_loan(self, receiver_address: str, assets: None, amounts: None, modes: None, on_behalf_of: str, params: bytes, referral_code: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.flashLoan(receiver_address, assets, amounts, modes, on_behalf_of, params, referral_code).build_transaction(override_tx_parameters)

    def get_addresses_provider(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getAddressesProvider().call()

    def get_configuration(self, asset: str) -> tuple:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getConfiguration(asset).call()

    def get_reserve_data(self, asset: str) -> tuple:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getReserveData(asset).call()

    def get_reserve_normalized_income(self, asset: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getReserveNormalizedIncome(asset).call()

    def get_reserve_normalized_variable_debt(self, asset: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getReserveNormalizedVariableDebt(asset).call()

    def get_reserves_list(self) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getReservesList().build_transaction()

    def get_user_account_data(self, user: str) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getUserAccountData(user).build_transaction()

    def get_user_configuration(self, user: str) -> tuple:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getUserConfiguration(user).call()

    def init_reserve(self, reserve: str, a_token_address: str, stable_debt_address: str, variable_debt_address: str, interest_rate_strategy_address: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.initReserve(reserve, a_token_address, stable_debt_address, variable_debt_address, interest_rate_strategy_address).build_transaction(override_tx_parameters)

    def liquidation_call(self, collateral_asset: str, debt_asset: str, user: str, debt_to_cover: int, receive_a_token: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.liquidationCall(collateral_asset, debt_asset, user, debt_to_cover, receive_a_token).build_transaction(override_tx_parameters)

    def paused(self) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.paused().call()

    def rebalance_stable_borrow_rate(self, asset: str, user: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.rebalanceStableBorrowRate(asset, user).build_transaction(override_tx_parameters)

    def repay(self, asset: str, amount: int, rate_mode: int, on_behalf_of: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.repay(asset, amount, rate_mode, on_behalf_of).build_transaction(override_tx_parameters)

    def set_configuration(self, reserve: str, configuration: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setConfiguration(reserve, configuration).build_transaction(override_tx_parameters)

    def set_pause(self, val: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setPause(val).build_transaction(override_tx_parameters)

    def set_reserve_interest_rate_strategy_address(self, reserve: str, rate_strategy_address: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setReserveInterestRateStrategyAddress(reserve, rate_strategy_address).build_transaction(override_tx_parameters)

    def set_user_use_reserve_as_collateral(self, asset: str, use_as_collateral: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setUserUseReserveAsCollateral(asset, use_as_collateral).build_transaction(override_tx_parameters)

    def swap_borrow_rate_mode(self, asset: str, rate_mode: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapBorrowRateMode(asset, rate_mode).build_transaction(override_tx_parameters)

    def withdraw(self, asset: str, amount: int, to: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.withdraw(asset, amount, to).build_transaction(override_tx_parameters)
