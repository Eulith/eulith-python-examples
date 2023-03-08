from typing import Optional, Union
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IUniswapV3Pool:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'indexed': True, 'internalType': 'int24', 'name': 'tickLower', 'type': 'int24'}, {'indexed': True, 'internalType': 'int24', 'name': 'tickUpper', 'type': 'int24'}, {'indexed': False, 'internalType': 'uint128', 'name': 'amount', 'type': 'uint128'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount0', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount1', 'type': 'uint256'}], 'name': 'Burn', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'indexed': False, 'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'indexed': True, 'internalType': 'int24', 'name': 'tickLower', 'type': 'int24'}, {'indexed': True, 'internalType': 'int24', 'name': 'tickUpper', 'type': 'int24'}, {'indexed': False, 'internalType': 'uint128', 'name': 'amount0', 'type': 'uint128'}, {'indexed': False, 'internalType': 'uint128', 'name': 'amount1', 'type': 'uint128'}], 'name': 'Collect', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'sender', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'indexed': False, 'internalType': 'uint128', 'name': 'amount0', 'type': 'uint128'}, {'indexed': False, 'internalType': 'uint128', 'name': 'amount1', 'type': 'uint128'}], 'name': 'CollectProtocol', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'sender', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount0', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount1', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'paid0', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'paid1', 'type': 'uint256'}], 'name': 'Flash', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint16', 'name': 'observationCardinalityNextOld', 'type': 'uint16'}, {'indexed': False, 'internalType': 'uint16', 'name': 'observationCardinalityNextNew', 'type': 'uint16'}], 'name': 'IncreaseObservationCardinalityNext', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint160', 'name': 'sqrtPriceX96', 'type': 'uint160'}, {'indexed': False, 'internalType': 'int24', 'name': 'tick', 'type': 'int24'}], 'name': 'Initialize', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'address', 'name': 'sender', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'indexed': True, 'internalType': 'int24', 'name': 'tickLower', 'type': 'int24'}, {'indexed': True, 'internalType': 'int24', 'name': 'tickUpper', 'type': 'int24'}, {'indexed': False, 'internalType': 'uint128', 'name': 'amount', 'type': 'uint128'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount0', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amount1', 'type': 'uint256'}], 'name': 'Mint', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint8', 'name': 'feeProtocol0Old', 'type': 'uint8'}, {'indexed': False, 'internalType': 'uint8', 'name': 'feeProtocol1Old', 'type': 'uint8'}, {'indexed': False, 'internalType': 'uint8', 'name': 'feeProtocol0New', 'type': 'uint8'}, {'indexed': False, 'internalType': 'uint8', 'name': 'feeProtocol1New', 'type': 'uint8'}], 'name': 'SetFeeProtocol', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'sender', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'indexed': False, 'internalType': 'int256', 'name': 'amount0', 'type': 'int256'}, {'indexed': False, 'internalType': 'int256', 'name': 'amount1', 'type': 'int256'}, {'indexed': False, 'internalType': 'uint160', 'name': 'sqrtPriceX96', 'type': 'uint160'}, {'indexed': False, 'internalType': 'uint128', 'name': 'liquidity', 'type': 'uint128'}, {'indexed': False, 'internalType': 'int24', 'name': 'tick', 'type': 'int24'}], 'name': 'Swap', 'type': 'event'}, {'inputs': [{'internalType': 'int24', 'name': 'tickLower', 'type': 'int24'}, {'internalType': 'int24', 'name': 'tickUpper', 'type': 'int24'}, {'internalType': 'uint128', 'name': 'amount', 'type': 'uint128'}], 'name': 'burn', 'outputs': [{'internalType': 'uint256', 'name': 'amount0', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amount1', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'int24', 'name': 'tickLower', 'type': 'int24'}, {'internalType': 'int24', 'name': 'tickUpper', 'type': 'int24'}, {'internalType': 'uint128', 'name': 'amount0Requested', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'amount1Requested', 'type': 'uint128'}], 'name': 'collect', 'outputs': [{'internalType': 'uint128', 'name': 'amount0', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'amount1', 'type': 'uint128'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'uint128', 'name': 'amount0Requested', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'amount1Requested', 'type': 'uint128'}], 'name': 'collectProtocol', 'outputs': [{'internalType': 'uint128', 'name': 'amount0', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'amount1', 'type': 'uint128'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'factory', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'fee', 'outputs': [{'internalType': 'uint24', 'name': '', 'type': 'uint24'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'feeGrowthGlobal0X128', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'feeGrowthGlobal1X128', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount0', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amount1', 'type': 'uint256'}, {'internalType': 'bytes', 'name': 'data', 'type': 'bytes'}], 'name': 'flash', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint16', 'name': 'observationCardinalityNext', 'type': 'uint16'}], 'name': 'increaseObservationCardinalityNext', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint160', 'name': 'sqrtPriceX96', 'type': 'uint160'}], 'name': 'initialize', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'liquidity', 'outputs': [{'internalType': 'uint128', 'name': '', 'type': 'uint128'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'maxLiquidityPerTick', 'outputs': [{'internalType': 'uint128', 'name': '', 'type': 'uint128'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'int24', 'name': 'tickLower', 'type': 'int24'}, {'internalType': 'int24', 'name': 'tickUpper', 'type': 'int24'}, {'internalType': 'uint128', 'name': 'amount', 'type': 'uint128'}, {'internalType': 'bytes', 'name': 'data', 'type': 'bytes'}], 'name': 'mint', 'outputs': [{'internalType': 'uint256', 'name': 'amount0', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'amount1', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': 'index', 'type': 'uint256'}], 'name': 'observations', 'outputs': [{'internalType': 'uint32', 'name': 'blockTimestamp', 'type': 'uint32'}, {'internalType': 'int56', 'name': 'tickCumulative', 'type': 'int56'}, {'internalType': 'uint160', 'name': 'secondsPerLiquidityCumulativeX128', 'type': 'uint160'}, {'internalType': 'bool', 'name': 'initialized', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint32[]', 'name': 'secondsAgos', 'type': 'uint32[]'}], 'name': 'observe', 'outputs': [{'internalType': 'int56[]', 'name': 'tickCumulatives', 'type': 'int56[]'}, {'internalType': 'uint160[]', 'name': 'secondsPerLiquidityCumulativeX128s', 'type': 'uint160[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'bytes32', 'name': 'key', 'type': 'bytes32'}], 'name': 'positions', 'outputs': [{'internalType': 'uint128', 'name': 'liquidity', 'type': 'uint128'}, {'internalType': 'uint256', 'name': 'feeGrowthInside0LastX128', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'feeGrowthInside1LastX128', 'type': 'uint256'}, {'internalType': 'uint128', 'name': 'tokensOwed0', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'tokensOwed1', 'type': 'uint128'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'protocolFees', 'outputs': [{'internalType': 'uint128', 'name': 'token0', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'token1', 'type': 'uint128'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint8', 'name': 'feeProtocol0', 'type': 'uint8'}, {'internalType': 'uint8', 'name': 'feeProtocol1', 'type': 'uint8'}], 'name': 'setFeeProtocol', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'slot0', 'outputs': [{'internalType': 'uint160', 'name': 'sqrtPriceX96', 'type': 'uint160'}, {'internalType': 'int24', 'name': 'tick', 'type': 'int24'}, {'internalType': 'uint16', 'name': 'observationIndex', 'type': 'uint16'}, {'internalType': 'uint16', 'name': 'observationCardinality', 'type': 'uint16'}, {'internalType': 'uint16', 'name': 'observationCardinalityNext', 'type': 'uint16'}, {'internalType': 'uint8', 'name': 'feeProtocol', 'type': 'uint8'}, {'internalType': 'bool', 'name': 'unlocked', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'int24', 'name': 'tickLower', 'type': 'int24'}, {'internalType': 'int24', 'name': 'tickUpper', 'type': 'int24'}], 'name': 'snapshotCumulativesInside', 'outputs': [{'internalType': 'int56', 'name': 'tickCumulativeInside', 'type': 'int56'}, {'internalType': 'uint160', 'name': 'secondsPerLiquidityInsideX128', 'type': 'uint160'}, {'internalType': 'uint32', 'name': 'secondsInside', 'type': 'uint32'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'recipient', 'type': 'address'}, {'internalType': 'bool', 'name': 'zeroForOne', 'type': 'bool'}, {'internalType': 'int256', 'name': 'amountSpecified', 'type': 'int256'}, {'internalType': 'uint160', 'name': 'sqrtPriceLimitX96', 'type': 'uint160'}, {'internalType': 'bytes', 'name': 'data', 'type': 'bytes'}], 'name': 'swap', 'outputs': [{'internalType': 'int256', 'name': 'amount0', 'type': 'int256'}, {'internalType': 'int256', 'name': 'amount1', 'type': 'int256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'int16', 'name': 'wordPosition', 'type': 'int16'}], 'name': 'tickBitmap', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'tickSpacing', 'outputs': [{'internalType': 'int24', 'name': '', 'type': 'int24'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'int24', 'name': 'tick', 'type': 'int24'}], 'name': 'ticks', 'outputs': [{'internalType': 'uint128', 'name': 'liquidityGross', 'type': 'uint128'}, {'internalType': 'int128', 'name': 'liquidityNet', 'type': 'int128'}, {'internalType': 'uint256', 'name': 'feeGrowthOutside0X128', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'feeGrowthOutside1X128', 'type': 'uint256'}, {'internalType': 'int56', 'name': 'tickCumulativeOutside', 'type': 'int56'}, {'internalType': 'uint160', 'name': 'secondsPerLiquidityOutsideX128', 'type': 'uint160'}, {'internalType': 'uint32', 'name': 'secondsOutside', 'type': 'uint32'}, {'internalType': 'bool', 'name': 'initialized', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'token0', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'token1', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def burn(self, tick_lower: None, tick_upper: None, amount: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.burn(tick_lower, tick_upper, amount).build_transaction(override_tx_parameters)

    def collect(self, recipient: str, tick_lower: None, tick_upper: None, amount0_requested: None, amount1_requested: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.collect(recipient, tick_lower, tick_upper, amount0_requested, amount1_requested).build_transaction(override_tx_parameters)

    def collect_protocol(self, recipient: str, amount0_requested: None, amount1_requested: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.collectProtocol(recipient, amount0_requested, amount1_requested).build_transaction(override_tx_parameters)

    def factory(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.factory().call()

    def fee(self) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.fee().build_transaction()

    def fee_growth_global0_x128(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.feeGrowthGlobal0X128().call()

    def fee_growth_global1_x128(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.feeGrowthGlobal1X128().call()

    def flash(self, recipient: str, amount0: int, amount1: int, data: bytes, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.flash(recipient, amount0, amount1, data).build_transaction(override_tx_parameters)

    def increase_observation_cardinality_next(self, observation_cardinality_next: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.increaseObservationCardinalityNext(observation_cardinality_next).build_transaction(override_tx_parameters)

    def initialize(self, sqrt_price_x96: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.initialize(sqrt_price_x96).build_transaction(override_tx_parameters)

    def liquidity(self) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.liquidity().build_transaction()

    def max_liquidity_per_tick(self) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.maxLiquidityPerTick().build_transaction()

    def mint(self, recipient: str, tick_lower: None, tick_upper: None, amount: None, data: bytes, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.mint(recipient, tick_lower, tick_upper, amount, data).build_transaction(override_tx_parameters)

    def observations(self, index: int) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.observations(index).build_transaction()

    def observe(self, seconds_agos: None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.observe(seconds_agos).build_transaction()

    def positions(self, key: bytes) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.positions(key).build_transaction()

    def protocol_fees(self) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.protocolFees().build_transaction()

    def set_fee_protocol(self, fee_protocol0: int, fee_protocol1: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setFeeProtocol(fee_protocol0, fee_protocol1).build_transaction(override_tx_parameters)

    def slot0(self) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.slot0().build_transaction()

    def snapshot_cumulatives_inside(self, tick_lower: None, tick_upper: None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.snapshotCumulativesInside(tick_lower, tick_upper).build_transaction()

    def swap(self, recipient: str, zero_for_one: bool, amount_specified: None, sqrt_price_limit_x96: None, data: bytes, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swap(recipient, zero_for_one, amount_specified, sqrt_price_limit_x96, data).build_transaction(override_tx_parameters)

    def tick_bitmap(self, word_position: None) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.tickBitmap(word_position).call()

    def tick_spacing(self) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.tickSpacing().build_transaction()

    def ticks(self, tick: None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.ticks(tick).build_transaction()

    def token0(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.token0().call()

    def token1(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.token1().call()
