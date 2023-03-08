import logging
from pprint import pprint
from typing import Any

import asn1
from botocore.exceptions import ClientError
from eth_keys.backends import BaseECCBackend, NativeECCBackend
from eth_keys.datatypes import PublicKey

from eulith_web3.signing import Signer, recover_v
from eth_keys.datatypes import Signature


class KmsSigner(Signer):
    def __init__(self, kms_client: Any, key_id: str, backend: BaseECCBackend = NativeECCBackend):
        self.key_id = key_id
        self.client = kms_client
        self.backend = backend
        try:
            key = self.client.get_public_key(KeyId=key_id)
        except ClientError as err:
            logging.error(
                "Couldn't get key '%s'. Here's why: %s",
                key_id, err.response['Error']['Message'])
            raise err
        pk_bytes = self.decode_pk(key['PublicKey'])
        self.public_address = PublicKey(pk_bytes, backend).to_checksum_address()

    @property
    def address(self):
        return self.public_address

    def sign_msg_hash(self, message_hash: bytes) -> 'Signature':
        der_sig = self.client.sign(KeyId=self.key_id, Message=message_hash, MessageType="DIGEST",
                                   SigningAlgorithm="ECDSA_SHA_256")
        decoder = asn1.Decoder()
        decoder.start(der_sig['Signature'])
        decoder.enter()
        _, r = decoder.read()
        _, s = decoder.read()
        return recover_v(r, s, message_hash, self.address, self.backend)

    def print_pk(self, key_id: str):
        try:
            key = self.client.get_public_key(KeyId=key_id)
        except ClientError as err:
            logging.error(
                "Couldn't get key '%s'. Here's why: %s",
                key_id, err.response['Error']['Message'])
        else:
            print(f"Got key {key_id}:")
            pprint(key)

    @staticmethod
    def decode_pk(pk_bytes) -> bytes:
        decoder = asn1.Decoder()
        decoder.start(pk_bytes)
        decoder.enter()
        decoder.enter()
        decoder.leave()
        tag, value = decoder.read()
        return value[1:]
