+++
title = "Nitro Enclaves CLI"
chapter = false
weight = 12
+++


**Nitro Enclaves CLI (Nitro CLI)** は Enclaves のライフサイクルを管理するツールです。Nitoro CLI で、Nitro Enclaves を作成、管理、終了することができます。Nitro CLI は親の EC2インスタンスにインストールする必要があります。

このセクションでは、Nitro CLI をどのように使用(enclaves を実行、管理、削除)するかを学び、また、デバッグモードで動作している時に enclave に接続する方法も確認できます。

このセクションでは、Nitro CLI を使用して enclave アプリケーションの Dockerイメージをビルドし、Dockerイメージを使用して Nitro enclave イメージファイルビルドし、enclave イメージファイルを使用して enclave を実行する方法を学習します。

![Architecture diagram](/images/nitro-enclaves-cli-arch.png)

### Nitro Enclave のリソースを確認する

1. Nitro Enclaves CLI が適切にインストールされていることを確認しましょう。
    ```sh
    $ nitro-cli --version
    ```
    **出力結果** は以下のようになるはずです
    <pre>Nitro CLI &lt;VERSION&gt;</pre>

    {{% notice tip %}}
CLI をインストールする詳細ステップは [前提条件と環境のセットアップ](../getting-started/prerequisites.html#install-and-configure-nitro-enclaves-cli-and-tools) のセクションを確認してください。
    {{% /notice %}}

1. Nitro Enclave 用のリソース(メモリと CPUs) を確認します。Nitro Enclave は Nitro Enclave アプリケーション用に親 EC2インスタンスの内部から特定のリソースを予約します。
    ```sh
    $ cat /etc/nitro_enclaves/allocator.yaml
    ```

    **出力結果** は以下のようになるはずです
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
デフォルトの値は `512MB` と `2 vCPUs` です。
    {{% /notice %}}

1. Nitro Enclave にリソースを割り当てた後に、親 EC2インスタンスで利用可能なメモリと CPU を確認しましょう。前提条件のセクションの `nitro-enclaves-allocator` を開始した場合は、それらはデフォルトの値で割り当てられます。
    ```sh
    $ free -m
    $ lscpu
    ```

    {{% notice info %}}
これらの値の変更を適用するには `nitro-enclaves-allocator` サービスを再起動する必要があります。x86 hyper-threaded のインスタンスでは、全ての CPUコア、すなわち 2つの vCPU を割り当てるべきです。
    {{% /notice %}}


### Nitro Enclave イメージファイルをビルドする

![Nitro enclave build process](/images/build-eif.png)
{{% notice note %}}
Nitro Enclaves では、アプリケーションをパッケージ化するための便利なファイルフォーマットとして、Dockerイメージを使用します。一般に、Dockerイメージは Dockerコンテナを作成するために使用されます。しかしここでは、enclave イメージファイルを作成するために Dockerイメージを使用します。
{{% /notice %}}

1. サンプルアプリケーションのための Dockerイメージをビルドしましょう。このセクションでは、`Hello World` を出力するシンプルな Python スクリプトを使用します。
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/nitro-enclaves-cli
    $ docker build -t hello-app:latest .
    ```

    **出力結果** は以下のようになるはずです
    <pre>
    Successfully tagged hello-app:latest
    </pre>

1. Dockerイメージを全てリストアップします。Dockerイメージの 1つとして `hello-app` が表示されます。
    ```sh
    $ docker image ls
    ```

1. それでは、Nitro Enclaveイメージをビルドしてみましょう。ここでは、`nitro-cli build-enclave` サブコマンドを使って、Dockerイメージを Nitro Enclaveイメージファイル(EIF) に変換します。以下のサブコマンドは、`hello.eif` という名前の Enclaveイメージファイルをビルドします。Dockerfile を含むローカルディレクトリか、Dockerリポジトリの中の Dockerイメージのどちらかを指定できます。このサブコマンドは、Enclaveイメージファイルごとの固有の値(SHA384ハッシュ) である `PCR0, PCR1, PCR2` のセットを返します。これらのハッシュ値は、Platform Configuration Registers(PCR) の形式で提供されます。PCR は enclave の身元証明(構成証明)プロセスで使用されます。

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

    例えば、Nitro Enclaves を AWS Key Management Service (KMS) と一緒に使用する場合、お客様が管理するキーポリシーの条件キーでこれらの PCR を指定できます。enclave 内のアプリケーションがサポートされている AWS KMS の操作を実行する際には、AWS KMS は操作を許可する前に、enclave の署名済み身元証明(構成証明)の中の PCR群と、KMS キーポリシーの条件キーで指定された PCR群を比較します。
    
    {{% notice tip %}}
このモジュールの [暗号技術を用いた身元証明(構成証明)](cryptographic-attestation.html) セクションで、これらの値の詳細を確認できます。
PCR の値の詳細な説明は、[公式ドキュメント](https://docs.aws.amazon.com/enclaves/latest/user/set-up-attestation.html) を確認してください。

    {{% /notice %}}

    ```sh
    $ nitro-cli build-enclave --docker-uri hello-app:latest --output-file hello.eif
    ```

    **出力結果** は以下のようになるはずです

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
`build-enclave` サブコマンドは Windows ではサポートされていません。Windows の親 EC2インスタンスを使用する場合は、Linux システムでこのサブコマンドを実行して、enclaveイメージファイル(.eif) を Windows の親 EC2インスタンスに転送する必要があります。
    {{% /notice %}}


### enclave を実行、接続、削除する

1. `run-enclave` サブコマンドは、enclave を作成するために、指定された数の vCPU とメモリ量を親の Amazon EC2インスタンスから区分けします。また、enclave 内で実行する OSライブラリとアプリケーションを含む `enclaveイメージファイル(.eif)` を提供する必要もあります。ログを見るために、開発環境で Enclaveアプリケーションを `debug` モードで実行します。アプリケーションログを確認するために enclaveコンソールにアクセスする必要がある場合は、`--debug-mode` オプションを含める必要があります。割り当てるメモリは、`EIF` のファイルサイズの 4倍以上にする必要があります。`/etc/nitro_enclaves/allocator.yaml` ファイルの `memory_mib` の値を `3072` に更新しなければならないことを意味します。さらに、最新のメモリ設定量を反映させるために、Nitro Enclave サービスの `nitro-enclaves-allocator` を再起動します。オプションで `EnclaveCID` つまり `vsock` ソケットで使用されるソケットアドレスを指定することもできます。`CIDs` には 4以上の値のみを指定できます。このオプションを省略した場合は、ランダムな `CID` が Enclave に割り当てられます。次のモジュールで、`vsock` つまりセキュアなローカルチャネルについて学習します。

    ```sh
    $ sudo systemctl stop nitro-enclaves-allocator.service
    $ ALLOCATOR_YAML=/etc/nitro_enclaves/allocator.yaml
    $ MEM_KEY=memory_mib
    $ DEFAULT_MEM=3072
    $ sudo sed -r "s/^(\s*${MEM_KEY}\s*:\s*).*/\1${DEFAULT_MEM}/" -i "${ALLOCATOR_YAML}"
    $ sudo systemctl start nitro-enclaves-allocator.service && sudo systemctl enable nitro-enclaves-allocator.service
    $ nitro-cli run-enclave --cpu-count 2 --memory 3072 --eif-path hello.eif --debug-mode --enclave-cid 16
    ```

    **出力結果** は以下のようになるはずです
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
Enclave の実行中に十分なメモリが割り当てられていない場合、次のようなエラーが表示されます。`[ E26 ] Insufficient memory requested. User provided `memory` is 1784 MB, but based on the EIF file size, the minimum memory should be 1792 MB`
    {{% /notice %}}


1. 稼働している enclaves の一覧を表示したり `EnclaveID` `ProcessID` `EnclaveCID` `State` `CPUIDs` `MemoryMiB` `Flags` のようなアトリビュートを表示するには、`describe-enclaves` コマンドを使います。

    ```sh
    $ nitro-cli describe-enclaves
    ```

    **出力結果** は以下のようになるはずです
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

1. 特定の enclave の `read-only` のコンソールに入ります。トラブルシューティングのために enclave のコンソール出力を表示できるようになります。このサブコマンドは、enclave 起動時に `--debug-mode` オプションを指定した時のみ使用できます。
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli console --enclave-id ${ENCLAVE_ID}
    ```

    **出力結果** は以下のようになるはずです

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

    デバッグモードの read-only コンソールから抜けるには `CTRL+C (^C)` を入力します。

1. Enclave を終了しましょう。
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
    ```
    **出力結果** は以下のようになるはずです
    <pre>
    Successfully terminated enclave i-0f83e6d2edfba9237-enc17a3112d0b4532b.
    {
    "EnclaveID": "i-0f83e6d2edfba9237-enc17a3112d0b4532b",
    "Terminated": true
    }
    </pre>

{{% notice tip %}}
Nitro Enclaves CLI サブコマンドの追加の詳細情報は、[公式ドキュメント](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave-cli-ref.html) を確認してください。
{{% /notice %}}

### サマリー

これで、簡単な Enclaveアプリケーションをビルドし実行する方法を確認できました。このセクションのコードを探索してみてください。その後は次のセクションに進み、親 EC2インスタンスと Nitro Enclave の間の `vsock` 通信チャネルについて学びます。

---
#### [セキュアなローカルチャネル](secure-local-channel.html) セクションに進んでください
