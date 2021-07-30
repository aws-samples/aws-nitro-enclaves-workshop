+++
title = "Troubleshooting"
chapter = false
weight = 15
+++

Now that you've had a chance to learn about cryptographic attestation with AWS Key Management Service (KMS). We'll now explore a few scenarios where we'll do some troubleshooting.

Let's terminate any enclaves that are running by first describing them and then terminating them:
```sh
$ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
$ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
```

### Exploring CLI errors

View current resources allocation for Nitro Enclaves:
```sh
$ cat /etc/nitro_enclaves/allocator.yaml
```

Let's reduce the memory allocation (`memory_mib`) to something small like `512MiB`:
```sh
$ sudo systemctl stop nitro-enclaves-allocator.service
$ ALLOCATOR_YAML=/etc/nitro_enclaves/allocator.yaml
$ MEM_KEY=memory_mib
$ DEFAULT_MEM=512
$ sudo sed -r "s/^(\s*${MEM_KEY}\s*:\s*).*/\1${DEFAULT_MEM}/" -i "${ALLOCATOR_YAML}"
$ sudo systemctl start nitro-enclaves-allocator.service && sudo systemctl enable nitro-enclaves-allocator.service
```

Validate that `memory_mib` was reduced:
```sh
$ cat /etc/nitro_enclaves/allocator.yaml
```
#### Attempt to run an enclave with less memory than required

Now, attempt to run the enclave with the memory allocated:
```sh
$ nitro-cli run-enclave --cpu-count 2 --memory 512 --eif-path ./data-processing.eif
```

Since the total size of the uncompressed enclave image file (EIF) is larger than the `512MiB` we allocated, we expect this to fail.

The **output** should look similar to
<pre>
[ E26 ] Insufficient memory requested. User provided `memory` is 512 MB, but based on the EIF file size, the minimum memory should be 2148 MB

For more details, please visit https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html#E26

If you open a support ticket, please provide the error log found at "/var/log/nitro_enclaves/err2021-06-18T21:46:43.249503129+00:00.log"
Failed connections: 1
[ E39 ] Enclave process connection failure. Such error appears when the enclave manager fails to connect to at least one enclave process for retrieving the description information.

For more details, please visit https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html#E39

If you open a support ticket, please provide the error log found at "/var/log/nitro_enclaves/err2021-06-18T21:46:43.249656960+00:00.log"
</pre>

This tells us two things:
1. There wasn't enough memory requested for the enclave to run based on the EIF size requirements.
1. The CLI couldn't retrieve information about the enclave it was requested to run.

#### Attempt to run an enclave with more memory than allocated

Attempt to run the enclave with more memory:
```sh
$ nitro-cli run-enclave --cpu-count 2 --memory 3072 --eif-path ./data-processing.eif
```

Since we allocated `512MiB` for the enclave from the parent EC2 instance and tried to run the enclave with `3072MiB`, we expect this to fail:

The **output** should look similar to
<pre>
Start allocating memory...
[ E27 ] Insufficient memory available. User provided `memory` is 3072 MB, which is more than the available hugepage memory.
You can increase the available memory by editing the `memory_mib` value from '/etc/nitro_enclaves/allocator.yaml' and then enable the nitro-enclaves-allocator.service.

For more details, please visit https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html#E27

If you open a support ticket, please provide the error log found at "/var/log/nitro_enclaves/err2021-06-18T20:56:47.554786281+00:00.log"
Failed connections: 1
[ E39 ] Enclave process connection failure. Such error appears when the enclave manager fails to connect to at least one enclave process for retrieving the description information.

For more details, please visit https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html#E39

If you open a support ticket, please provide the error log found at "/var/log/nitro_enclaves/err2021-06-18T20:56:47.554962083+00:00.log"
</pre>
This tells us two things:
1. There wasn't enough memory allocated and available for the enclave to run based on the `run-enclave` subcommand requirements.
1. The CLI couldn't retrieve information about the enclave it was requested to run.

{{% notice note %}}
Similar to the memory errors above, there are also a set of errors for when you run into conditions and limits around CPU allocation.
{{% /notice %}}
#### Nitro Enclaves CLI error codes

The Nitro Enclaves CLI includes the `explain` subcommand, which displays detailed information. You can use this to print information locally about the error. For example:

```sh
$ nitro-cli explain --error-code E26
```
The **output** should look similar to
<pre>
Insufficient memory requested. Such error appears when the user requests to launch an enclave with not enough memory. The enclave memory should be at least equal to the size of the EIF file used for launching the enclave.
        Example: (EIF file size: 11MB) `nitro-cli run-enclave --cpu-count 2 --memory 5 --eif-path /path/to/my/eif`. In this case, the user requested to run an enclave with only 5MB of memory, whereas the EIF file alone requires 11MB.
</pre>

{{% notice tip %}}
For additional details on all the error codes, see [Documentation](https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html).
{{% /notice %}}

---
#### Proceed to the [Module cleanup](module-cleanup.html) section to continue the workshop.
