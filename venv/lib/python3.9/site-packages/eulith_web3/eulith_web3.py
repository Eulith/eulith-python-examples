import time
import urllib.parse
from urllib.parse import urljoin
import uuid
from typing import Union, Any, cast, Callable, Dict, Optional, List

import requests
import web3.middleware
from eth_typing import URI, ChecksumAddress
from eth_utils import is_hex_address
from requests import Response
from web3 import Web3, HTTPProvider
from web3.types import RPCEndpoint, RPCResponse, TxParams

from eulith_web3.common import INT_FEE_TO_FLOAT_DIVISOR
from eulith_web3.erc20 import TokenSymbol, EulithWETH, EulithERC20
from eulith_web3.exceptions import EulithAuthException, EulithRpcException
from eulith_web3.requests import EulithShortOnRequest, EulithShortOffRequest, EulithAaveV2StartLoanRequest, FlashRequest
from eulith_web3.swap import EulithSwapProvider, EulithSwapRequest, EulithLiquiditySource
from eulith_web3.uniswap import EulithUniswapV3Pool, EulithUniV3StartLoanRequest, EulithUniV3StartSwapRequest, \
    EulithUniV3SwapQuoteRequest, EulithUniswapPoolLookupRequest, UniswapPoolFee


class ApiToken:
    def __init__(self, token: str, expire: int) -> None:
        self.token = token
        self.expire = expire

    def expires_in_hours(self) -> float:
        now = int(time.time())
        return (self.expire - now) / 3600


def get_api_access_token(eulith_url: URI, eulith_refresh_token: str) -> ApiToken:
    headers = {"Authorization": "Bearer " + eulith_refresh_token, "Content-Type": "application/json"}
    url = urljoin(eulith_url, URI("v0/api/access"))
    response = requests.get(url, headers=headers)
    handle_http_response(response)
    json = response.json()
    token = ApiToken(json['token'], json['exp'])
    return token


def handle_http_response(resp: Response):
    if resp.status_code == 400:
        raise EulithAuthException(f"status: {str(resp.status_code)}, message: {resp.text}")
    if resp.status_code != 200:
        raise EulithRpcException(f"status: {str(resp.status_code)}, message: {resp.text}")


def handle_rpc_response(resp: RPCResponse):
    if 'error' in resp and resp['error'] != "":
        raise EulithRpcException("RPC Error: " + str(resp['error']))


def add_params_to_url(url: str, params) -> str:
    url_parts = urllib.parse.urlparse(url)
    query = dict(urllib.parse.parse_qsl(url_parts.query))
    query.update(params)

    return url_parts._replace(query=urllib.parse.urlencode(query)).geturl()


def get_headers(url: str, token: str) -> Dict:
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    if 'localhost' in url:
        headers['X-Test'] = 'true'

    return headers


class EulithData:
    def __init__(self, eulith_url: Union[URI, str],
                 eulith_refresh_token: str, private: bool) -> None:
        self.eulith_url: URI = URI(eulith_url)
        self.private = private
        self.eulith_refresh_token: str = eulith_refresh_token
        self.atomic: bool = False
        self.tx_id: str = ""
        self.api_access_token: ApiToken = get_api_access_token(self.eulith_url, self.eulith_refresh_token)
        headers = get_headers(eulith_url, self.api_access_token.token)
        self.http = HTTPProvider(endpoint_uri=eulith_url, request_kwargs={
            'headers': headers,
            'timeout': 60
        })

    def send_transaction(self, params) -> RPCResponse:
        try:
            return self.http.make_request(RPCEndpoint("eth_sendTransaction"), params)
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    def start_transaction(self, account: str, gnosis: str):
        self.atomic = True
        self.tx_id = str(uuid.uuid4())
        params = {'auth_address': account, 'atomic_tx_id': self.tx_id}
        if len(gnosis) > 0:
            params['gnosis_address'] = gnosis
        new_url = add_params_to_url(self.eulith_url, params)
        self.http.endpoint_uri = new_url

    def commit(self) -> TxParams:
        self.atomic = False  # we need to do this even if things fail
        params = {}
        try:
            response = self.http.make_request(RPCEndpoint("eulith_commit"), params)
            handle_rpc_response(response)
            self.tx_id = ""
            return cast(TxParams, response['result'])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    def rollback(self):
        self.commit()

    def refresh_api_token(self):
        self.api_access_token: ApiToken = get_api_access_token(self.eulith_url, self.eulith_refresh_token)
        headers = get_headers(self.eulith_url, self.api_access_token.token)
        self.http = HTTPProvider(endpoint_uri=self.eulith_url, request_kwargs={
            'headers': headers
        })

    def is_close_to_expiry(self) -> bool:
        return self.api_access_token.expires_in_hours() < 6

    def swap_quote(self, params: EulithSwapRequest) -> (bool, RPCResponse):
        try:
            sell_token: EulithERC20
            buy_token: EulithERC20
            sell_amount: float
            recipient: Optional[ChecksumAddress]
            route_through: Optional[EulithSwapProvider]
            slippage_tolerance: Optional[float]
            liquidity_source: Optional[EulithLiquiditySource]

            sell_address = params.get('sell_token').address
            buy_address = params.get('buy_token').address
            parsed_params = {
                'sell_token': sell_address,
                'buy_token': buy_address,
                'sell_amount': params.get('sell_amount')
            }
            recipient = params.get('recipient', None)
            route_through = params.get('route_through', None)
            liquidity_source = params.get('liquidity_source', None)
            slippage_tolerance = params.get('slippage_tolerance', None)

            if recipient:
                parsed_params['recipient'] = recipient
            if route_through:
                parsed_params['route_through'] = route_through
            if liquidity_source:
                parsed_params['liquidity_source'] = liquidity_source
            if slippage_tolerance:
                parsed_params['slippage_tolerance'] = slippage_tolerance

            return True, self.http.make_request(RPCEndpoint("eulith_swap"), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def short_on(self, params: EulithShortOnRequest) -> (bool, RPCResponse):
        try:
            collateral_address = params.get('collateral_token').address
            short_address = params.get('short_token').address
            parsed_params = {
                'collateral_token': collateral_address,
                'short_token': short_address,
                'collateral_amount': params.get('collateral_amount')
            }

            return True, self.http.make_request(RPCEndpoint("eulith_short_on"), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def short_off(self, params: EulithShortOffRequest) -> (bool, RPCResponse):
        try:
            collateral_address = params.get('collateral_token').address
            short_address = params.get('short_token').address
            parsed_params = {
                'collateral_token': collateral_address,
                'short_token': short_address,
                'repay_short_amount': params.get('repay_short_amount'),
                'true_for_unwind_a': params.get('true_for_unwind_a', True)
            }

            return True, self.http.make_request(RPCEndpoint("eulith_short_off"), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def start_uniswap_v3_loan(self, params: EulithUniV3StartLoanRequest) -> (bool, RPCResponse):
        try:
            borrow_token_a = params.get('borrow_token_a').address
            borrow_amount_a = params.get('borrow_amount_a')
            borrow_token_b = params.get('borrow_token_b', None)
            borrow_amount_b = params.get('borrow_amount_b', None)
            pay_transfer_from = params.get('pay_transfer_from', None)
            recipient = params.get('recipient', None)

            parsed_params = {
                'borrow_token_a': borrow_token_a,
                'borrow_amount_a': borrow_amount_a
            }

            if borrow_token_b:
                parsed_params['borrow_token_b'] = borrow_token_b.address
            if borrow_amount_b:
                parsed_params['borrow_amount_b'] = borrow_amount_b
            if pay_transfer_from:
                parsed_params['pay_transfer_from'] = pay_transfer_from
            if recipient:
                parsed_params['recipient'] = recipient

            return True, self.http.make_request(RPCEndpoint('eulith_start_uniswapv3_loan'), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def start_uniswap_v3_swap(self, params: EulithUniV3StartSwapRequest) -> (bool, RPCResponse):
        try:
            sell_token = params.get('sell_token').address
            amount = params.get('amount')
            pool_address = params.get('pool_address')
            fill_or_kill = params.get('fill_or_kill')
            sqrt_limit_price = params.get('sqrt_limit_price')
            recipient = params.get('recipient', None)
            pay_transfer_from = params.get('pay_transfer_from', None)

            parsed_params = {
                'sell_token': sell_token,
                'amount': amount,
                'pool_address': pool_address,
                'fill_or_kill': fill_or_kill,
                'sqrt_limit_price': sqrt_limit_price
            }

            if recipient:
                parsed_params['recipient'] = recipient
            if pay_transfer_from:
                parsed_params['pay_transfer_from'] = pay_transfer_from

            return True, self.http.make_request(RPCEndpoint('eulith_start_uniswapv3_swap'), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def start_aave_v2_loan(self, params: EulithAaveV2StartLoanRequest) -> (bool, RPCResponse):
        try:
            tokens = params.get('tokens')
            token_params = []
            for t in tokens:
                token_params.append({
                    'token_address': t.get('token_address').address,
                    'amount': t.get('amount')
                })

            parsed_params = {
                'tokens': token_params,
            }

            return True, self.http.make_request(RPCEndpoint('eulith_start_aavev2_loan'), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def finish_inner(self) -> (bool, RPCResponse):
        try:
            return True, self.http.make_request(RPCEndpoint('eulith_finish_inner'), None)
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def uniswap_v3_quote(self, params: EulithUniV3SwapQuoteRequest) -> (bool, RPCResponse):
        try:
            parsed_params = {
                'sell_token': params.get('sell_token').address,
                'buy_token': params.get('buy_token').address,
                'amount': params.get('amount'),
                'true_for_amount_in': params.get('true_for_amount_in', True)
            }

            fee = params.get('fee', None)
            if fee:
                parsed_params['fee'] = fee.value

            return True, self.http.make_request(RPCEndpoint('eulith_uniswapv3_quote'), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def lookup_univ3_pool(self, params: EulithUniswapPoolLookupRequest) -> (bool, RPCResponse):
        try:
            parsed_params = {
                'token_a': params.get('token_a').address,
                'token_b': params.get('token_b').address,
                'fee': params.get('fee').value
            }
            return True, self.http.make_request(RPCEndpoint('eulith_uniswapv3_pool_lookup'), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def lookup_token_symbol(self, symbol: TokenSymbol) -> (bool, ChecksumAddress, int):
        try:
            res = self.http.make_request(RPCEndpoint("eulith_erc_lookup"), [{'symbol': symbol}])
            parsed_res = res.get('result', [])
            if len(parsed_res) != 1:
                return False, RPCResponse(error=f"unexpected response for {symbol} lookup, token isn't recognized")
            return True, parsed_res[0].get('contract_address'), parsed_res[0].get('decimals')
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)


class EulithWeb3(Web3):
    def __init__(self,
                 eulith_url: Union[URI, str],
                 eulith_refresh_token: str,
                 signing_middle_ware: Any = None,
                 private: bool = False,
                 **kwargs
                 ) -> None:
        if signing_middle_ware:
            eulith_url = add_params_to_url(eulith_url, {'auth_address': signing_middle_ware.address})

        self.eulith_data = EulithData(eulith_url, eulith_refresh_token, private)
        http = self._make_http()
        kwargs.update(provider=http)
        super().__init__(**kwargs)

        if signing_middle_ware:
            self.middleware_onion.add(signing_middle_ware)
        self.middleware_onion.add(eulith_atomic_middleware)
        self.middleware_onion.add(web3.middleware.request_parameter_normalizer)
        self.middleware_onion.add(web3.middleware.pythonic_middleware, "eulith_pythonic")
        self.middleware_onion.add(eulith_api_token_middleware)

        self.v0 = v0(self)

    def _eulith_send_atomic(self, params) -> RPCResponse:
        return self.eulith_data.send_transaction(params)

    def eulith_start_transaction(self, account: str, gnosis: str = "") -> None:
        if not is_hex_address(account):
            raise TypeError("account must be a hex formatted address")
        if len(gnosis) > 0 and not is_hex_address(gnosis):
            raise TypeError("gnosis must either be blank or a hex formatted address")
        self.eulith_data.start_transaction(account, gnosis)

    def eulith_commit_transaction(self) -> TxParams:
        return self.eulith_data.commit()

    def eulith_rollback_transaction(self):
        self.eulith_data.rollback()

    def eulith_contract_address(self, account: str) -> str:
        if not is_hex_address(account):
            raise TypeError("account must be a hex formatted address")
        params = {}
        try:
            response = self.manager.provider.make_request("eulith_get_contracts", params)
            handle_rpc_response(response)
            contracts = response['result']['contracts']
            for c in contracts:
                if c['authorized_address'].lower() == account.lower():
                    return c['contract_address']
            return ""
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    def eulith_create_contract_if_not_exist(self, account: str) -> str:
        c = self.eulith_contract_address(account)
        if c == "":
            c = self.eulith_create_contract(account)

        return c

    def eulith_create_contract(self, account: str) -> str:
        if not is_hex_address(account):
            raise TypeError("account must be a hex formatted address")
        params = [{'authorized_address': account}]
        try:
            response = self.manager.provider.make_request("eulith_new_contract", params)
            handle_rpc_response(response)
            result = response['result']
            self.eth.wait_for_transaction_receipt(result['new_contract_tx_hash'])

            return result['contract_address']
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    def eulith_refresh_api_token(self):
        self.eulith_data.refresh_api_token()
        http = self._make_http()
        self.provider = http

    def eulith_refresh_api_token_if_necessary(self):
        if self.eulith_data.is_close_to_expiry():
            self.eulith_refresh_api_token()

    def eulith_swap_quote(self, params: EulithSwapRequest) -> (float, List[TxParams]):
        status, res = self.eulith_data.swap_quote(params)
        if status:
            price = res.get('result', {}).get('price', 0.0)
            txs = res.get('result', {}).get('txs', [])
            return price, txs
        else:
            raise EulithRpcException(res)

    def _make_http(self):
        url = self.eulith_data.eulith_url
        if self.eulith_data.private:
            url = add_params_to_url(url, {'private': 'true'})

        headers = get_headers(url, self.eulith_data.api_access_token.token)

        http = HTTPProvider(endpoint_uri=url, request_kwargs={
            'headers': headers
        })

        return http

    def eulith_send_multi_transaction(self, txs: [TxParams]):
        for tx in txs:
            tx_hash = self.eth.send_transaction(tx)
            if not self.eulith_data.atomic:
                self.eth.wait_for_transaction_receipt(tx_hash)

    def eulith_get_erc_token(self, symbol: TokenSymbol) -> Union[EulithERC20, EulithWETH]:
        status, contract_address_or_error, decimals = self.eulith_data.lookup_token_symbol(symbol)
        if status:
            if symbol == TokenSymbol.WETH:
                return EulithWETH(self, contract_address_or_error)
            else:
                return EulithERC20(self, contract_address_or_error, decimals)
        else:
            raise EulithRpcException(contract_address_or_error)

    # returns price (float), fee (UniswapPoolFee), swap_request (EulithUniV3StartSwapRequest)
    def parse_uni_quote_to_swap_request(self, res, fill_or_kill: bool, recipient: Optional[ChecksumAddress],
                                        pay_transfer_from: Optional[ChecksumAddress]) -> (float, UniswapPoolFee, EulithUniV3StartSwapRequest):
        result = res.get('result')
        price = result.get('price')
        sell_token_address = result.get('sell_token')
        sell_token = EulithERC20(self, sell_token_address)
        amount = result.get('amount')
        pool_address = result.get('pool_address')
        limit_price = result.get('sqrt_limit_price')
        fee = result.get('fee')
        true_for_amount_in = result.get('true_for_amount_in')

        if not true_for_amount_in:
            amount *= -1.0  # make negative if we want exact amount out

        swap_request = EulithUniV3StartSwapRequest(sell_token=sell_token,
                                                   amount=amount,
                                                   pool_address=self.toChecksumAddress(pool_address),
                                                   fill_or_kill=fill_or_kill,
                                                   sqrt_limit_price=limit_price,
                                                   recipient=recipient,
                                                   pay_transfer_from=pay_transfer_from)

        return price, UniswapPoolFee(fee), swap_request


# Namespace
class v0:
    def __init__(self, ew3: EulithWeb3):
        self.ew3 = ew3

    def send_multi_transaction(self, txs: [TxParams]):
        self.ew3.eulith_send_multi_transaction(txs)

    def start_atomic_transaction(self, account: str, gnosis: str = "") -> None:
        return self.ew3.eulith_start_transaction(account, gnosis)

    def commit_atomic_transaction(self) -> TxParams:
        return self.ew3.eulith_commit_transaction()

    def rollback_atomic_transaction(self):
        return self.ew3.eulith_rollback_transaction()

    def get_toolkit_contract_address(self, account: str) -> str:
        return self.ew3.eulith_contract_address(account)

    def ensure_toolkit_contract(self, account: str) -> str:
        return self.ew3.eulith_create_contract_if_not_exist(account)

    def create_toolkit_contract(self, account: str) -> str:
        return self.ew3.eulith_create_contract(account)

    def refresh_api_token(self):
        self.ew3.eulith_refresh_api_token()

    def ensure_valid_api_token(self):
        self.ew3.eulith_refresh_api_token_if_necessary()

    def get_erc_token(self, symbol: TokenSymbol) -> Union[EulithERC20, EulithWETH]:
        return self.ew3.eulith_get_erc_token(symbol)

    def get_swap_quote(self, params: EulithSwapRequest) -> (float, List[TxParams]):
        return self.ew3.eulith_swap_quote(params)

    def short_on(self, params: EulithShortOnRequest) -> float:
        status, res = self.ew3.eulith_data.short_on(params)
        if status:
            leverage = res.get('result', {}).get('leverage', 0.0)
            return leverage
        else:
            raise EulithRpcException(res)

    def short_off(self, params: EulithShortOffRequest) -> float:
        status, res = self.ew3.eulith_data.short_off(params)
        if status:
            released_collateral = res.get('result', {}).get('released_collateral', 0.0)
            return released_collateral
        else:
            raise EulithRpcException(res)

    def get_univ3_pool(self, params: EulithUniswapPoolLookupRequest) -> EulithUniswapV3Pool:
        status, res = self.ew3.eulith_data.lookup_univ3_pool(params)
        if status:
            result = res.get('result')
            if len(result) != 1:
                raise EulithRpcException(f"uniswap v3 pool lookup came back with an unexpected response: {result}")
            inner_result = result[0]

            token_zero = inner_result.get('token_zero')
            token_one = inner_result.get('token_one')
            fee = inner_result.get('fee')
            pool_address = inner_result.get('pool_address')
            return EulithUniswapV3Pool(self.ew3, self.ew3.toChecksumAddress(pool_address), UniswapPoolFee(fee),
                                       self.ew3.toChecksumAddress(token_zero), self.ew3.toChecksumAddress(token_one))
        else:
            raise EulithRpcException(res)

    # returns fee (float) as percent: i.e. 0.001 = 0.1%
    def start_flash_loan(self, params: Union[EulithUniV3StartLoanRequest, EulithAaveV2StartLoanRequest]) -> float:
        param_keys = params.keys()
        if 'borrow_token_a' in param_keys:
            status, res = self.ew3.eulith_data.start_uniswap_v3_loan(params)
        else:
            status, res = self.ew3.eulith_data.start_aave_v2_loan(params)

        if status:
            fee = int(res.get('result'), 16)
            return fee / INT_FEE_TO_FLOAT_DIVISOR
        else:
            raise EulithRpcException(res)

    # returns fee (float) as percent: i.e. 0.001 = 0.1%
    def start_uni_swap(self, params: EulithUniV3StartSwapRequest) -> float:
        status, res = self.ew3.eulith_data.start_uniswap_v3_swap(params)
        if status:
            fee = int(res.get('result'), 16)
            return fee / INT_FEE_TO_FLOAT_DIVISOR
        else:
            raise EulithRpcException(res)

    # returns price (float), fee (float), swap_request (EulithUniV3StartSwapRequest)
    def get_univ3_best_price_quote(self, sell_token: EulithERC20, buy_token: EulithERC20, amount: float,
                                   true_for_amount_in: Optional[bool] = True, fill_or_kill: Optional[bool] = True,
                                   recipient: Optional[ChecksumAddress] = None, pay_transfer_from: Optional[ChecksumAddress] = None) -> (float, float, EulithUniV3StartSwapRequest):
        parsed_params = EulithUniV3SwapQuoteRequest(
            sell_token=sell_token,
            buy_token=buy_token,
            amount=amount,
            true_for_amount_in=true_for_amount_in,
            fee=None)
        status, res = self.ew3.eulith_data.uniswap_v3_quote(parsed_params)
        if status:
            price, fee, swap_request = self.ew3.parse_uni_quote_to_swap_request(res, fill_or_kill, recipient, pay_transfer_from)
            return price, fee / INT_FEE_TO_FLOAT_DIVISOR, swap_request
        else:
            raise EulithRpcException(res)

    def finish_inner(self) -> int:
        status, res = self.ew3.eulith_data.finish_inner()
        if status:
            return int(res.get('result'), 16)
        else:
            raise EulithRpcException(res)

    # returns price (float), fee (float) as percent: i.e. 0.001 = 0.1%
    def start_flash(self, params: FlashRequest) -> (float, float):
        amount = params.get('take_amount')
        pay_transfer_from = params.get('pay_transfer_from', None)
        recipient = params.get('recipient', None)

        if params.get('take').address.lower() == params.get('pay').address.lower():
            fee = self.start_flash_loan(EulithUniV3StartLoanRequest(
                borrow_token_a=params.get('take'),
                borrow_amount_a=amount,
                borrow_token_b=None,
                borrow_amount_b=None,
                pay_transfer_from=pay_transfer_from,
                recipient=recipient
            ))

            return 1.0, fee
        else:
            price, fee, swap_request = self.get_univ3_best_price_quote(params.get('pay'),
                                                                       params.get('take'),
                                                                       amount,
                                                                       False, True, recipient, pay_transfer_from)
            fee = self.start_uni_swap(swap_request)
            return price, fee

    def pay_flash(self) -> int:
        return self.finish_inner()


def eulith_atomic_middleware(
        make_request: Callable[[RPCEndpoint, Any], Any], web3: "Web3") -> Callable[[RPCEndpoint, Any], RPCResponse]:
    def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
        try:
            if method != "eth_sendTransaction" or not web3.eulith_data.atomic:
                return make_request(method, params)

            return cast(EulithWeb3, web3)._eulith_send_atomic(params)
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    return middleware


def eulith_api_token_middleware(
        make_request: Callable[[RPCEndpoint, Any], Any], web3: "Web3"
) -> Callable[[RPCEndpoint, Any], RPCResponse]:
    def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
        try:
            ew3 = cast(EulithWeb3, web3)
            ew3.eulith_refresh_api_token_if_necessary()

            return make_request(method, params)
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    return middleware
