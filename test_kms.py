import boto3
from eulith_web3.kms import KmsSigner

if __name__ == '__main__':
    aws_credentials_profile_name = '...'
    key_name = '...'
    formatted_key_name = f'alias/{key_name}'

    session = boto3.Session(profile_name=aws_credentials_profile_name)
    client = session.client('kms')
    kms_signer = KmsSigner(client, formatted_key_name)

    print(kms_signer.address)
