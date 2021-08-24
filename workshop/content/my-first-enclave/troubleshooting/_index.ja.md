+++
title = "トラブルシューティング"
chapter = false
weight = 15
+++

ここまでに、AWS Key Management Service (KMS)を使った暗号技術を用いた身元証明(構成証明)について学習する機会がありました。ここからは、トラブルシューティングのためのシナリオをいくつかご紹介します。

実行中の enclaves の情報を表示(describe-enclaves) してから削除しましょう:
```sh
$ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
$ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
```

### CLI のエラーを調べます

現時点での Nitro Enclaves 向けのリソース割り当て状況を確認します:
```sh
$ cat /etc/nitro_enclaves/allocator.yaml
```

メモリ割り当て量 (`memory_mib`) を `512MiB` などに小さくしてみます:
```sh
$ sudo systemctl stop nitro-enclaves-allocator.service
$ ALLOCATOR_YAML=/etc/nitro_enclaves/allocator.yaml
$ MEM_KEY=memory_mib
$ DEFAULT_MEM=512
$ sudo sed -r "s/^(\s*${MEM_KEY}\s*:\s*).*/\1${DEFAULT_MEM}/" -i "${ALLOCATOR_YAML}"
$ sudo systemctl start nitro-enclaves-allocator.service && sudo systemctl enable nitro-enclaves-allocator.service
```

`memory_mib` が小さくなったことを確認します:
```sh
$ cat /etc/nitro_enclaves/allocator.yaml
```
#### 要求されるメモリよりも少ないメモリで起動してみます

ここでは、メモリ割り当て量を指定して enclave を起動しようとしています:
```sh
$ nitro-cli run-enclave --cpu-count 2 --memory 512 --eif-path ./data-processing.eif
```

圧縮されていない enclave イメージファイル(EIF) の合計サイズは割り当てた `512MiB` よりも大きいので、起動に失敗すると予想できます。

**出力結果** は以下のようになるはずです
<pre>
[ E26 ] Insufficient memory requested. User provided `memory` is 512 MB, but based on the EIF file size, the minimum memory should be 2148 MB

For more details, please visit https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html#E26

If you open a support ticket, please provide the error log found at "/var/log/nitro_enclaves/err2021-06-18T21:46:43.249503129+00:00.log"
Failed connections: 1
[ E39 ] Enclave process connection failure. Such error appears when the enclave manager fails to connect to at least one enclave process for retrieving the description information.

For more details, please visit https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html#E39

If you open a support ticket, please provide the error log found at "/var/log/nitro_enclaves/err2021-06-18T21:46:43.249656960+00:00.log"

</pre>
2つのことを示しています:
1. EIF サイズの要件に基づいて enclave を実行するための十分なメモリがありませんでした。
1. 実行するために必要な enclave に関する情報を CLI は取得できませんでした。

#### 割り当てられたメモリ量よりも大きな値で enclave を起動しようとする

より多くのメモリで enclave を起動しようとします:
```sh
$ nitro-cli run-enclave --cpu-count 2 --memory 3072 --eif-path ./data-processing.eif
```

親 EC2インスタンスから enclave に `512MiB` を割り当てた状態で、enclave を `3072MiB` で起動しようと試みたために、以下のように失敗します:

**出力結果** は以下のようになるはずです
<pre>
Start allocating memory...
[ E27 ] Insufficient memory available. User provided `memory` is 3072 MB, which is more than the available hugepage memory.
You can increase the available memory by editing the `memory_mib` value from '/etc/nitro_enclaves/allocator.yaml' and then enable the nitro-enclaves-allocator.service.

For more details, please visit https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html#E27

If you open a support ticket, please provide the error log found at "/var/log/nitro_enclaves/err2021-06-18T20:56:47.554786281+00:00.log"
Failed connections: 1
[ E39 ] Enclave process connection failure. Such error appears when the enclave manager fails to connect to at least one enclave process for retrieving the description information.

For more details, please visit https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html#E39
<-- さらに詳細な情報は https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html#E39 で確認してください。-->

If you open a support ticket, please provide the error log found at "/var/log/nitro_enclaves/err2021-06-18T20:56:47.554962083+00:00.log"
<-- サポートケースを起案する場合、"/var/log/nitro_enclaves/err2021-06-18T20:56:47.554962083+00:00.log" のようなエラーログを提供してください。-->
</pre>
2つのことを示しています:
1. `run-enclave` サブコマンドが要求した値で enclave を起動するために必要なメモリ量が割り当てられておらず使用できなかった。
1. CLI は enclave の起動に必要な enclave に関する情報を取得できなかった。

{{% notice note %}}
上記のメモリのエラーと同様に、CPU の割り当ての条件や制限に関するエラーが発生することもあります。
{{% /notice %}}
#### Nitro Enclaves CLI エラーコード

Nitro Enclaves CLI には、詳細な情報を表示するための `explain` サブコマンドがあります。手元の環境でエラーに関する情報を表示させることができます。例えば:

```sh
$ nitro-cli explain --error-code E26
```
**出力結果** は以下のようになるはずです
<pre>
Insufficient memory requested. Such error appears when the user requests to launch an enclave with not enough memory. The enclave memory should be at least equal to the size of the EIF file used for launching the enclave.
        Example: (EIF file size: 11MB) `nitro-cli run-enclave --cpu-count 2 --memory 5 --eif-path /path/to/my/eif`. In this case, the user requested to run an enclave with only 5MB of memory, whereas the EIF file alone requires 11MB.
</pre>

{{% notice tip %}}
全てのエラーコードに関する詳細情報は、[公式ドキュメント](https://docs.aws.amazon.com/enclaves/latest/user/cli-errors.html) を確認してください。
{{% /notice %}}

---
#### [モジュールの後片付け](module-cleanup.html) セクションに進んでください。
