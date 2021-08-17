+++
title = "モジュールの後片付け"
chapter = false
weight = 16
+++

{{% notice info %}}
これが最後に実行するモジュールの場合は、Workshop の環境を片付けるために [後片付け](../cleanup.html) に進んでください。
{{% /notice %}}

* 実行している enclave を削除します。
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
    ```

* Nitro Enclaves allocator サービスの設定を元に戻します。

    ```sh
    $ sudo systemctl stop nitro-enclaves-allocator.service
    $ ALLOCATOR_YAML=/etc/nitro_enclaves/allocator.yaml
    $ MEM_KEY=memory_mib
    $ CPU_KEY=cpu_count
    $ DEFAULT_MEM=512
    $ DEFAULT_CPU=2
    $ sudo sed -r "s/^(\s*${MEM_KEY}\s*:\s*).*/\1${DEFAULT_MEM}/" -i "${ALLOCATOR_YAML}"
    $ sudo sed -r "s/^(\s*${CPU_KEY}\s*:\s*).*/\1${DEFAULT_CPU}/" -i "${ALLOCATOR_YAML}"
    $ sudo systemctl start nitro-enclaves-allocator.service && sudo systemctl enable nitro-enclaves-allocator.service
    ```

---
#### [後片付け](../cleanup.html) に進みます。
