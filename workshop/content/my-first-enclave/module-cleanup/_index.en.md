+++
title = "Module cleanup"
chapter = false
weight = 16
+++

{{% notice info %}}
If this is the last module you will be executing, please go to the [Cleanup](../cleanup.html) module to finalize the cleanup of your workshop environment.
{{% /notice %}}

* Terminate the running enclave.
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
    ```

* Revert Nitro Enclaves allocator service configuration changes.

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
#### Proceed to the [Cleanup](../cleanup.html) module to continue the workshop.