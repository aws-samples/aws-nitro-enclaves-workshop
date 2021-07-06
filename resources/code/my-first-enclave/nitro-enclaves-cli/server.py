# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# // SPDX-License-Identifier: MIT-0

import time

def main():
    count = 1
    while True:
        print(f"[{count:4d}] Hello from the enclave side!")
        count += 1
        time.sleep(5)

if __name__ == '__main__':
    main()
