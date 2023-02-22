import os
import sys

import boto3
from botocore import exceptions
from eulith_web3.kms import KmsSigner

sys.path.insert(0, os.getcwd())
from utils.banner import print_banner

"""
NOTE: in order to run.sh this example, you must have a correctly configured KMS key with AWS credentials in your ~/.aws
directory. See https://www.loom.com/share/6cf2ba73f14847758f1551223cbe7a28, or get in touch with us for help with this.
"""
if __name__ == '__main__':
    print_banner()

    aws_credentials_profile_name = 'default'

    # YOU CAN PUT YOUR KEY NAME HERE, OTHERWISE YOU WILL BE PROMPTED FOR IT
    key_name = '<THE_NAME_OF_YOUR_KEY_GOES_HERE>'

    if key_name == '<THE_NAME_OF_YOUR_KEY_GOES_HERE>':
        key_name = input('Enter the name of your KMS key: ')

    formatted_key_name = f'alias/{key_name}'

    session = boto3.Session(profile_name=aws_credentials_profile_name)
    client = session.client('kms')

    try:
        kms_signer = KmsSigner(client, formatted_key_name)
    except exceptions.NoCredentialsError:
        print(f'Was not able to locate aws credentials for profile '
              f'{aws_credentials_profile_name} in ~/.aws/credentials\n')
        exit(1)

    print(f'KMS wallet address: {kms_signer.address}')
