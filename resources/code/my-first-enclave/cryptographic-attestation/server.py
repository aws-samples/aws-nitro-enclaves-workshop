# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# // SPDX-License-Identifier: MIT-0

import boto3
import json
import base64
import socket
import subprocess

KMS_PROXY_PORT="8000"

def get_plaintext(credentials):
    """
    prepare inputs and invoke decrypt function
    """

    # take all data from client
    access = credentials['access_key_id']
    secret = credentials['secret_access_key']
    token = credentials['token']
    ciphertext= credentials['ciphertext']
    region = credentials['region']
    creds = decrypt_cipher(access, secret, token, ciphertext, region)
    return creds


def decrypt_cipher(access, secret, token, ciphertext, region):
    """
    use KMS Tool Enclave Cli to decrypt cipher text
    """
    proc = subprocess.Popen(
    [
        "/app/kmstool_enclave_cli",
        "--region", region,
        "--proxy-port", KMS_PROXY_PORT,
        "--aws-access-key-id", access,
        "--aws-secret-access-key", secret,
        "--aws-session-token", token,
        "--ciphertext", ciphertext,
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

    ret = proc.communicate()

    if ret[0]:
        b64text = proc.communicate()[0].decode()
        plaintext = base64.b64decode(b64text).decode()
        return plaintext
    else:
        return "KMS Error. Decryption Failed."


def main():


    s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
    cid = socket.VMADDR_CID_ANY
    port = 5000
    s.bind((cid, port))
    s.listen()
    print(f"Started server on port {port} and cid {cid}")

    while True:
        c, addr = s.accept()
        payload = c.recv(4096)
        r = {}
        credentials = json.loads(payload.decode())

        plaintext = get_plaintext(credentials)
        print(plaintext)

        if plaintext == "KMS Error. Decryption Failed.":
            r["error"] = plaintext
        else:
            last_four = plaintext[-4:]
            r["last_four"] = last_four

        c.send(str.encode(json.dumps(r)))

        c.close()

if __name__ == '__main__':
    main()
