+++
title = "セキュアなローカルチャネル"
chapter = false
weight = 13
+++

このセクションでは、Nitro Enclave と外部のエンドポイント間の通信をセットアップします。初期状態では、Nitro Enclave は親インスタンスとだけしか通信できませんし、安全なローカル通信チャネルである vsock 経由でしか通信できません。Nitro Enclave が外部エンドポイントと通信できるようにするには、親インスタンス上で動作する proxy サーバと、Nitro Enclave 内部で動作する Traffic-Forwarder を実行します。これらは、vsock を経由してくる Enclave からのトラフィックを、外部のエンドポイントに転送します。

このサンプルでは、Nitro Enclave の中で動作するサンプルサーバーアプリケーションを実行し、enclave から外部のウェブサイトにアクセスさせるための vsock-proxy でフォワーダを設定します。
クライアントアプリケーションは、Nitro Enclave 内で動作しポート番号 `5005` で待ち受けるサーバーアプリケーションにアクセスします。ローカルループバックでは、サーバーアプリケーションからの全てのトラフィックを Traffic-Forwarder (ポート番号 `443`) に転送し、そこから vsock-proxy (ポート番号 `8001`) に転送します。vsock-proxy は、ターゲットとなる外部のエンドポイントにトラフィックをルーティングします。応答されたレスポンスは、クライアントアプリケーションに戻ってきます。どちらのタイプの実行でも (クライアント - サーバーでも Enclave - エンドポイントでも) vsock ソケットを経由することになります。

![Architecture diagram](/images/secure-local-channel-arch.png)


{{% notice info %}}
** vsock とは何か、そしてどのように enclave と通信するか？** - vsock は context ID (CID) とポート番号で定義されるソケットインターフェイスの一種です。context ID (CID) は TCP/IP 接続における IPアドレスのようなものです。vsockは、標準的で一意に定義されている POSIX ソケット API (すなわち connect、listen、accept など) を利用して enclave と通信します。アプリケーションはこれらの API を使用することで、vsock 上でネイティブに通信することもできますし、プロキシを経由して vsock 上で HTTPリクエストを送信することもできます。** vsock ソケット** - vsock は親インスタンスと enclave の間のローカルなコミュニケーションチャネルです。これは、enclave が外部サービスと対話する際に使用できる唯一のコミュニケーションチャネルです。enclave の vsock アドレスは、enclave を起動する時に指定する context identifier (CID) で定義されます。親インスタンスで使用される CID は常に 3 です。
**Vsock-Proxy** - 親インスタンスのネットワークを経由して外部のエンドポイントにアクセスするために、Nitro enclave は vsock プロキシを使用します。この Workshop では、Nitro CLI に付属する vsock-proxy の実装を使用します。後のモジュールで Nitro Enclaves SDK を使用して AWS KMS を操作 (`kms-decrypt` `kms-generate-data-key` `kms-generate-random`)するために使用するので、このモジュールの例ではカスタムエンドポイントと通信することにフォーカスします。KMS とのセッションは、AWS KMS と enclave 自身との間で論理的に確立され、すべてのセッショントラフィックは親インスタンスから保護されます。
{{% /notice %}}


### ソースコードのレビュー

まず初めに、提供されたサンプルコードを見てみましょう。コードのフォルダに移動してください:

```sh
$ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/secure-local-channel/
```

サンプルのソースコードを見てみましょう。ターゲットイメージを定義する `Dockerfile`、アプリケーションの "ビジネスロジック" が含まれている `traffic_forwarder.py` `server.py`、サーバとフォワーダの双方をセットアップし実行する `run.sh`、enclave 外部からサーバにアクセスするための `client.py` のみが含まれています。
 
Traffic-Forwarder はこの Workshop において as-is で(現状のままで)提供されるカスタムコードです。これは Nitro Enclave の中で分離されたコンポーネントとして動作し、Nitro Enclave 内部からの全ての通信を vsock-proxy や他のエンドポイントにルーティングします。

Traffic-Forwarder の全てのコードは `code/traffic_forwarder.py` に保存されています。下記でローカルポートのフォワーディングを設定します:
1. IPアドレスをローカルループバックに設定します
1. ターゲットサイトへの通信をローカルループバックに向けるために hosts レコードを追加します

この設定により、Traffic-Forwarder がトラフィックを vsock-proxy へとルーティングできるようになります。


### VSOCK Proxy の実行
1. 前提条件のセクションにて、Nitro Enclaves CLI のインストールの一環として、すでに `vsock-proxy` をインストールし設定しています。以下のコマンドを実行することで `vsock-proxy` がシステムで有効になっているかどうかを確認できます:
    ```sh
    $ vsock-proxy --help
    ```
    `vsock-proxy` を実行するために利用可能なパラメータ群を確認してください。

    {{% notice info %}}
この Workshop の範囲外ですが、CLI と `vsock-proxy` をソースコードと Amazon Linux repository の双方からインストールできます。詳細は、[Nitro Enclaves CLI GitHub repository](https://github.com/aws/aws-nitro-enclaves-cli) で確認できます。
    {{% /notice %}}

1. デフォルトでは、提供される `vsock-proxy` は、全ての AWSリージョンのそれぞれの KMS エンドポイントのポート `443` のみへのルーティングを許可します。この挙動は、(`/etc/vsock_proxy/config.yaml` で確認できる) 設定ファイルの allowlist で制限されています。しかしながら、今回の例では、プロキシを別のウェブエンドポイントに向けてみることにします。サンプルコードの `vsock-proxy.yaml` を使うこともできますし、以下のコマンドを実行してカスタムファイルを作成することもできます:
    ```sh
    $ echo "allowlist:" >> your-vsock-proxy.yaml
    $ echo "- {address: ip-ranges.amazonaws.com, port: 443}" >> your-vsock-proxy.yaml
    ```
    上記のコマンドで生成されるコンフィグファイルは、`vsock-proxy` に対して `ip-ranges.amazonaws.com` のポート443 への通信のみを許可します。

1. 以下のコマンドで `vsock-proxy` を開始します (設定ファイルをパラメータとして指定できます):
    ```sh
    $ vsock-proxy 8001 ip-ranges.amazonaws.com 443 --config your-vsock-proxy.yaml
    ```

### サーバーアプリケーションの起動
1. 現在のターミナルセッションで vsock-proxy を起動させたまま、サーバーアプリケーションを起動するために新規のターミナルセッションを起動します。(新規のターミナルセッションを起動するには、メニューバーで **Window** / **New Terminal** を選択します。)

1. `secure-local-channel` コードのディレクトリに移動します:
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/secure-local-channel/
    ```

1. これまでのセクションで学んだステップを再度実行して、サーバーアプリケーションをビルドしましょう。docker イメージをビルドするために以下のコマンドを実行し、enclave イメージファイルを作成し、デバッグモードで新規の enclave を実行し、デバッグコンソールにアクセスします:
    ```sh
    $ docker build ./ -t secure-channel-example
    $ nitro-cli build-enclave --docker-uri secure-channel-example:latest --output-file secure-channel-example.eif
    $ nitro-cli run-enclave --cpu-count 2 --memory 2048 --eif-path secure-channel-example.eif --debug-mode
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli console --enclave-id ${ENCLAVE_ID}
    ```

    {{% notice info %}}
enclave がより多くの使用可能メモリ量を要求するような場合には、`/etc/nitro_enclaves/allocator.yaml` を設定変更し、allocator サービスを再起動する必要があります。詳細は [Nitro CLI 公式ドキュメント](https://github.com/aws/aws-nitro-enclaves-cli) を確認してください。
    {{% /notice %}}

### クライアントアプリケーションの実行
vsock-proxy とサーバーアプリケーションが動作している状態で、ホスト上で動作しているクライアントアプリケーションを実行してみましょう。クライアントアプリケーションは、AWS S3 サービスの公開IPレンジのリストを取得し、クライアント実行の最後のパラメータとして指定したリージョンだけをフィルタします。

1. 新規のターミナルセッションを開始します (新規のターミナルセッションを開始するには、メニューバーで **Window** / **New Terminal** を選択し)実行します:

1. `secure-local-channel` コードのディレクトリに移動し、下記のコマンドを実行してクライアントアプリケーションを開始します:
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/secure-local-channel/
    $ ENCLAVE_CID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveCID")
    $ python3 client.py client ${ENCLAVE_CID} 5005 "us-east-1"
    ```

    クライアントアプリケーションを実行することで、指定したリージョンの S3 サービス向けに公開された IPアドレスレンジだけをフィルタして表示します。

    {{% notice note %}}
クライアントアプリケーションは 3つのパラメータ: `cid` `port` `query` を処理します。`port` と `query` を制御できますが、`cid` は Nitro Enclave を起動する時だけ変更可能です。enclave の CID は、`nitro-cli describe-enclaves` を実行することで確認できます。
    {{% /notice %}}

### Summary
### サマリー
親インスタンスでは、ポート `8001` をリッスンし全てのトラフィックをカスタム HTTPS エンドポイントへ転送する vsock-proxy を構築しました。enclave の中では、traffic forwarder が localhost のポート`443` への全てのトラフィックを受け入れ、トラフィックを vsock-proxy へと転送します。

### 次のモジュールの準備
次のモジュールへと進む前に、既存の Nitro Enclaves を停止しデフォルトの設定で vsock-proxy を起動し直してください (KMS エンドポイントにアクセスするように戻ります)

1. enclave を終了しましょう:
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
    ```

1. `vsock-proxy` のターミナルセッションで、変更した設定で動作している `vsock-proxy` を停止するために `CTRL+C (^C)` を押下します。

1. デフォルトの設定 `/etc/vsock_proxy/config.yaml` で `vsock-proxy` を起動するために、以下のコマンドを実行します:
    ```sh
    $ sudo systemctl enable nitro-enclaves-vsock-proxy.service
    $ sudo systemctl start nitro-enclaves-vsock-proxy.service
    ```
proxy はデフォルトの設定 `/etc/vsock_proxy/config.yaml` ポート番号 `8000` で起動し、インスタンスが動作する AWS リージョンの AWS KMS エンドポイントにプロキシするようになります。

---
#### [暗号技術を用いた身元証明(構成証明)](cryptographic-attestation.html) セクションに進んでください。
