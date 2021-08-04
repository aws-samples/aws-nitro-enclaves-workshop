+++
title = "Nitro Enclaves CLI"
chapter = false
weight = 12
+++


The **Nitro Enclaves CLI (Nitro CLI)** is a command-line tool for managing the lifecycle of enclaves. You can use the Nitro CLI to create, manage, and terminate Nitro Enclaves. The Nitro CLI must be installed on the Amazon EC2 parent instance. 

In this section, you learn how to use the Nitro CLI to build a Docker image of your enclave application, use the Docker image to build your Nitro enclave image file, run an enclave in debug-mode using the enclave image file and connect to enclave console to check debug logs.


![Architecture diagram](/images/nitro-enclaves-cli-arch.png)

### Verify Nitro Enclave resources

1. Let's verify that Nitro Enclaves CLI is installed correctly.
    ```sh
    $ nitro-cli --version
    ```
    The **output** should look similar to
    <pre>Nitro CLI &lt;VERSION&gt;</pre>

    {{% notice tip %}}
For detailed steps on installing the CLI, see [Prerequisites and environment setup](../getting-started/prerequisites.html#install-and-configure-nitro-enclaves-cli-and-tools) section.
    {{% /notice %}}

1. Check resources (memory and CPUs) for your Nitro Enclave. Nitro Enclave reserves the specified resources within the parent EC2 instance for the Nitro Enclave application.
    ```sh
    $ cat /etc/nitro_enclaves/allocator.yaml
    ```

    The **output** should look similar to
    <pre>
    # Enclave configuration file.
    #
    # How much memory to allocate for enclaves (in MiB).
    memory_mib: 512
    #
    # How many CPUs to reserve for enclaves.
    cpu_count: 2
    #
    # Alternatively, the exact CPUs to be reserved for the enclave can be explicitely
    # configured by using `cpu_pool` (like below), instead of `cpu_count`.
    # Note: cpu_count and cpu_pool conflict with each other. Only use exactly one of them.
    # Example of reserving CPUs 2, 3, and 6 through 9:
    # cpu_pool: 2,3,6-9
    </pre>

    {{% notice info %}}
The default values are `512MB` and `2 vCPUs`.
    {{% /notice %}}

1. Let's check available memory and CPU on the parent EC2 instance after you have allocated resources to Nitro Enclave. The resources were allocated with default values when you started `nitro-enclaves-allocator` service in the pre-requisites section.
    ```sh
    $ free -m
    $ lscpu
    ```

    {{% notice info %}}
The changes require restarting `nitro-enclaves-allocator` service. You should allocate CPU in full cores i.e., 2x vCPU for x86 hyper-threaded instances. 
    {{% /notice %}}


### Build Nitro Enclave Image File

![Nitro enclave build process](/images/build-eif.png)
{{% notice note %}}
Nitro Enclaves uses Docker images as a convenient file format for packaging your applications. Docker images are typically used to create Docker containers. However, in this case, you use the Docker image to create an enclave image file instead.
{{% /notice %}}

1. Let's build a Docker image for your sample application. For this section, we'll use a simple Python implementation of `Hello World` to get started.
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/nitro-enclaves-cli
    $ docker build -t hello-app:latest .
    ```

    The **output** should look similar to
    <pre>
    Successfully tagged hello-app:latest
    </pre>

1. List all Docker images. It shows `hello-app` as one of the Docker images.
    ```sh
    $ docker image ls
    ```

1. Now, let's build the Nitro Enclave image. We'll convert the Docker image to a Nitro Enclave Image File (EIF) by using the `nitro-cli build-enclave` subcommand. The following subcommand builds an enclave image file named `hello.eif`. You can specify either a local directory containing a Dockerfile or a Docker image in a Docker repository. The subcommand returns a set of measurements (SHA384 hashes) - `PCR0, PCR1 and PCR2` that are unique to the enclave image file. These measurements are provided in the form of Platform Configuration Registers (PCRs). The PCRs are used during the enclave's attestation process.

    <table style="width:100%">
    <tr>
        <th>PCR</th>
        <th>Hash Of</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>PCR0</td>
        <td>Enclave image file</td>
        <td>A contiguous measure of the contents of the image file, without the section data.</td>
    </tr>
    <tr>
        <td>PCR1</td>
        <td>Linux kernel and bootstrap</td>
        <td>A contiguous measurement of the kernel and boot ramfs data.</td>
    </tr>
        <tr>
        <td>PCR2</td>
        <td>Application</td>
        <td>A contiguous, in-order measurement of the user applications, without the boot ramfs.</td>
    </tr>
    </table>

    For example, when using Nitro Enclaves with AWS Key Management Service (KMS), you can specify these PCRs in condition keys for customer-managed keys policies. When an application in the enclave performs a supported AWS KMS operation, AWS KMS compares the PCRs in the enclave's signed attestation document with the PCRs specified in the condition keys of the KMS key policy before allowing the operation.

    {{% notice tip %}}
You will learn more about the significance of these values in [Cryptographic attestation](cryptographic-attestation.html) section of this module.  
For detailed explanation of PCR values, see [Documentation](https://docs.aws.amazon.com/enclaves/latest/user/set-up-attestation.html).
    {{% /notice %}}

    ```sh
    $ nitro-cli build-enclave --docker-uri hello-app:latest --output-file hello.eif
    ```

    The **output** should look similar to below

    <pre>
    Start building the Enclave Image...
    Enclave Image successfully created.
    {
    "Measurements": {
        "HashAlgorithm": "Sha384 { ... }",
        "PCR0": "7a381d54de75c1d205259756f6b3327b310a425842758d28c1addaebf22e519725c036dd9471d823992e7e51acce55d0",
        "PCR1": "c35e620586e91ed40ca5ce360eedf77ba673719135951e293121cb3931220b00f87b5a15e94e25c01fecd08fc9139342",
        "PCR2": "0621aa3fbdf7e59eab3a3b95ea01b766a94e9016ed42a75b1369859097fe481eb2ff678a63ec0e131c9acea60ca92486"
    }
    }
    </pre>


    {{% notice info %}}
The `build-enclave` subcommand is not supported on Windows. If you are using a Windows parent instance, you must run this subcommand on a Linux system and then transfer the enclave image file (.eif) to the Windows parent instance.
    {{% /notice %}}


### Run, connect, and terminate the enclave

1. The `run-enclave` subcommand partitions the specified number of vCPUs and the amount of memory from the Amazon EC2 parent instance to create the enclave. You also need to provide an `enclave image file (.eif)` that contains the operating system libraries and the application that you want to run inside the enclave. Run your Enclave application in `debug` mode in the development environment to look at the logs. If you need to access the enclave console to see the application logs, so you must include the `--debug-mode` option. The allocated memory should be greater than four times of the `EIF` file size. This means you have to update the value of `memory_mib` to `3072` in `/etc/nitro_enclaves/allocator.yaml` file. Furthermore, restart Nitro Enclave Service `nitro-enclaves-allocator` to reflect the latest memory values. You can optionally specify `EnclaveCID` i.e. the socket address used by the `vsock` socket. Only `CIDs` of 4 and higher can be specified. If you omit this option, a random `CID` is allocated to the enclave. You will learn more about `vsock`, i.e. secure local channel in the next module.

    ```sh
    $ sudo systemctl stop nitro-enclaves-allocator.service
    $ ALLOCATOR_YAML=/etc/nitro_enclaves/allocator.yaml
    $ MEM_KEY=memory_mib
    $ DEFAULT_MEM=3072
    $ sudo sed -r "s/^(\s*${MEM_KEY}\s*:\s*).*/\1${DEFAULT_MEM}/" -i "${ALLOCATOR_YAML}"
    $ sudo systemctl start nitro-enclaves-allocator.service && sudo systemctl enable nitro-enclaves-allocator.service
    $ nitro-cli run-enclave --cpu-count 2 --memory 3072 --eif-path hello.eif --debug-mode --enclave-cid 16
    ```

    The **output** should look similar to
    <pre>
    Start allocating memory...
    Started enclave with enclave-cid: 16, memory: 3072 MiB, cpu-ids: [1, 3]
    {
    "EnclaveID": "i-xxxxxx-enc17a3112d0b4532b",
    "ProcessID": 5685,
    "EnclaveCID": 16,
    "NumberOfCPUs": 2,
    "CPUIDs": [
        1,
        3
    ],
    "MemoryMiB": 3072
    }
    </pre>

    {{% notice info %}}
If you don't allocate enough memory while running enclave then you will see a error similar to `[ E26 ] Insufficient memory requested. User provided `memory` is 1784 MB, but based on the EIF file size, the minimum memory should be 1792 MB`
    {{% /notice %}}


1. Use `describe-enclaves` command to list running Enclaves and display associated attributes such as `EnclaveID`, `ProcessID`, `EnclaveCID`, `State`, `CPUIDs`, `MemoryMiB` and `Flags`. 

    ```sh
    $ nitro-cli describe-enclaves
    ```

    The **output** should look similar to
    <pre>
    [
        {
            "EnclaveID": "i-xxxxxx-enc17a35be0c1e837f",
            "ProcessID": 6576,
            "EnclaveCID": 16,
            "NumberOfCPUs": 2,
            "CPUIDs": [
            1,
            3
            ],
            "MemoryMiB": 3072,
            "State": "RUNNING",
            "Flags": "DEBUG_MODE"
        }
    ]
    </pre>

1. Enter a `read-only` console for the specified enclave. This enables you to view the enclave's console output to assist with troubleshooting. You can use this subcommand only on an enclave that was launched with the `--debug-mode` flag.
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli console --enclave-id ${ENCLAVE_ID}
    ```

    The **output** should look similar to

    <pre>
    Connecting to the console for enclave 24...
    Successfully connected to the console.
    [    0.000000] Linux version 4.14.177-104.253.amzn2.x86_64 (mockbuild@ip-10-0-1-32) (gcc version 7.3.1 20180712 (Red Hat 7.3.1-6) (GCC)) #1 SMP Fri May 1 02:01:13 UTC 2020
    ...
    [    0.879922] Loaded X.509 cert 'Build time autogenerated kernel key: c582bb2a1fdabdd195bbc9c8840fff8158852907'
    [    0.881222] zswap: loaded using pool lzo/zbud
    [    0.882014] Key type encrypted registered
    [    0.883766] Freeing unused kernel memory: 1300K
    [    0.904028] Write protecting the kernel read-only data: 14336k
    [    0.906239] Freeing unused kernel memory: 2016K
    [    0.907754] Freeing unused kernel memory: 476K
    [    0.908625] nsm: loading out-of-tree module taints kernel.
    [    0.909337] nsm: module verification failed: signature and/or required key missing - tainting kernel
    [    0.915484] random: python3: uninitialized urandom read (24 bytes read)
    ...
    [   1] Hello from the enclave side!
    [   2] Hello from the enclave side!
    [   3] Hello from the enclave side!
    [   4] Hello from the enclave side!
    [   5] Hello from the enclave side!
    </pre>

    Press `CTRL+C (^C)` to exit the debug mode read-only console output.

1. Let's terminate the enclave.
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
    ```
    The **output** should look similar to
    <pre>
    Successfully terminated enclave i-0f83e6d2edfba9237-enc17a3112d0b4532b.
    {
    "EnclaveID": "i-0f83e6d2edfba9237-enc17a3112d0b4532b",
    "Terminated": true
    }
    </pre>

{{% notice tip %}}
For additional details on the Nitro Enclaves CLI subcommands, see [Documentation](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave-cli-ref.html).
{{% /notice %}}

### Summary

You have now seen how to build and run a simple Enclave application. Feel free to explore the code for this section. Then, proceed to the next section to learn about the `vsock` communication channel between the parent instance and the Nitro Enclave.

---
#### Proceed to the [Secure local channel](secure-local-channel.html) section to continue the workshop.
