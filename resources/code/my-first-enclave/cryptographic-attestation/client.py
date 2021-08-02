# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# // SPDX-License-Identifier: MIT-0

import boto3
import json
import base64
from random import randrange
import socket
import subprocess
import argparse
import requests


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alias", required=True, help="valid KMS key alias")
    parser.add_argument(
        "--values",
        type=argparse.FileType('r'),
        help='The account values file to select an account number from')
    parser.add_argument(
        "--ciphertext",
        type=argparse.FileType('r'),
        help='A file containing a kms-encrypted base64 encoded account number')
    arg_group = parser.add_mutually_exclusive_group(required=True)
    arg_group.add_argument(
        "--prepare",
        action="store_true",
        help="select a single account number and encrypt it using KMS")
    arg_group.add_argument(
        "--submit",
        action="store_true",
        help=
        "submit an encrypted account number to the enclave server application")

    return parser.parse_args()


def get_identity_document():
    """
    Get identity document for current EC2 Host
    """
    r = requests.get(
        "http://169.254.169.254/latest/dynamic/instance-identity/document")
    return r


def get_region(identity):
    """
    Get account of current instance identity
    """
    region = identity.json()["region"]
    return region


def get_account(identity):
    """
    Get account of current instance identity
    """
    region = identity.json()["accountId"]
    return region


def set_identity():
    identity = get_identity_document()
    region = get_region(identity)
    account = get_account(identity)
    return region, account


def prepare_server_request(ciphertext):
    """
    Get the AWS credential from EC2 instance metadata
    """
    r = requests.get(
        "http://169.254.169.254/latest/meta-data/iam/security-credentials/")
    instance_profile_name = r.text

    r = requests.get(
        "http://169.254.169.254/latest/meta-data/iam/security-credentials/%s" %
        instance_profile_name)
    response = r.json()

    print(ciphertext)

    credential = {
        'access_key_id': response['AccessKeyId'],
        'secret_access_key': response['SecretAccessKey'],
        'token': response['Token'],
        'region': REGION,
        'ciphertext': ciphertext
    }

    return credential


def get_cid():
    """
    Determine CID of Current Enclave
    """
    proc = subprocess.Popen(["/bin/nitro-cli", "describe-enclaves"],
                            stdout=subprocess.PIPE)
    output = json.loads(proc.communicate()[0].decode())
    enclave_cid = output[0]["EnclaveCID"]
    return enclave_cid


def parse_input(values):
    arr = values.read().splitlines()
    values.close()
    return arr


def select_random_value(arr):
    arr_len = len(arr)
    rand_val = arr[randrange(arr_len)]
    return rand_val


def encrypt_string(string, alias, kms):
    encrypted_string = kms.encrypt(KeyId=f"alias/{alias}", Plaintext=string)
    binary_cipher_text = encrypted_string[u"CiphertextBlob"]
    base64_cipher_text = base64.b64encode(binary_cipher_text)
    print(base64_cipher_text.decode())
    print(string[-4:])
    return base64_cipher_text.decode()


REGION, ACCOUNT = set_identity()


def main():

    args = parse_args()

    if args.prepare is True:
        kms = boto3.client("kms", region_name=REGION)
        arr = parse_input(args.values)
        rand_val = select_random_value(arr)
        base64_cipher_text = encrypt_string(rand_val, args.alias, kms)
        file = open("string.encrypted", "w")
        file.write(base64_cipher_text)
        file.close
        exit()
    elif args.submit is True:
        ciphertext = args.ciphertext.read()

        # Get EC2 instance metedata and prepare JSON to send to server
        credential = prepare_server_request(ciphertext)

        # Create a vsock socket object
        s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)

        # Get CID from command line parameter
        cid = get_cid()

        # The port should match the server running in enclave
        port = 5000

        # Connect to the server
        s.connect((cid, port))

        # Send AWS credential to the server running in enclave
        s.send(str.encode(json.dumps(credential)))

        # receive data from the server
        r = s.recv(4096).decode()

        #parse response
        parsed = json.loads(r)

        #pretty print response
        print(json.dumps(parsed, indent=4, sort_keys=True))

        # close the connection
        s.close()
    else:
        print('valid arguments not given')
        exit()


if __name__ == '__main__':
    main()
