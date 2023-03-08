import logging

from eth_keys.backends import NativeECCBackend, BaseECCBackend
from eth_keys.datatypes import PublicKey, Signature
from eth_utils import big_endian_to_int
from fireblocks_sdk import FireblocksSDK, RawMessage, UnsignedMessage

from hexbytes import HexBytes

from eulith_web3.signing import Signer, SigningException

logger = logging.getLogger(__name__)

ALGO: str = 'MPC_ECDSA_SECP256K1'
COMPRESSED: int = 0


class FireblocksSigner(Signer):
    def __init__(self, api_private_key: str, api_key: str, vault_acct_id: int, api_base_url="https://api.fireblocks.io",
                 backend: BaseECCBackend = NativeECCBackend):
        self.fireblocks = FireblocksSDK(api_private_key, api_key, api_base_url=api_base_url)
        self.vault_acct_id = vault_acct_id
        self.derivation_path = "[44,60," + str(vault_acct_id) + ",0,0]"
        pub_key = self.fireblocks.get_public_key_info(ALGO, self.derivation_path, COMPRESSED)
        actual_pk = PublicKey(HexBytes(pub_key['publicKey'][2:]), backend)
        self.public_address = actual_pk.to_checksum_address()
        logger.info("Fireblocks signer for ethereum address %s", self.public_address)
        self.backend = backend

    @property
    def address(self):
        return self.public_address

    def sign_msg_hash(self, message_hash: bytes) -> 'Signature':
        raw = RawMessage([UnsignedMessage(message_hash.hex(),
                                          derivationPath=[44, 60, self.vault_acct_id, 0, 0])], algorithm=ALGO)
        tx_result = self.fireblocks.create_raw_transaction(raw)
        # pprint(tx_result)
        tx_id = tx_result['id']
        tx = self.fireblocks.get_transaction_by_id(tx_id)
        while tx['status'] == "SUBMITTED" or tx['status'] == "QUEUED" or tx['status'].startswith("PENDING"):
            tx = self.fireblocks.get_transaction_by_id(tx_id)

        if tx['status'] != "COMPLETED":
            raise SigningException("Unexpected Fireblocks transaction status ", tx['status'], tx['subStatus'])

        # untested after this point:
        signature = tx['signedMessages'][0]['signature']

        r = big_endian_to_int(HexBytes(signature['r']))
        s = big_endian_to_int(HexBytes(signature['s']))
        v = int(signature['v'])
        return Signature(vrs=(v, r, s), backend=self.backend)
