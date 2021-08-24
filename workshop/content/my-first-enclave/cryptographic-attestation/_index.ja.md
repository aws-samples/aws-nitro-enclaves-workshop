+++
title = "暗号技術を用いた構成証明(身元証明)"
chapter = false
weight = 14
+++


このセクションでは、Nitro Enclaves の暗号技術を用いた構成証明(身元証明)と AWS KMS を利用したアプリケーションを体験します。このアプリケーションは、Enclave の中で機密データの処理を行うサンプルです。このサンプルを使って、機密データを保護するための構成証明の利用方法を説明します。まず最初は、構成証明を利用せずにビルド・デプロイして動作を理解します。その後に構成証明を活用して、Nitro Enclave 内の処理の分離がどのように強化されるかを見ていきます。

### Nitro Enclaves のユニークな機能

Nitro Enclaves SDK を使用すると、Enclave は固有の測定値を含んだ暗号署名付きの構成証明ドキュメントを Nitro Hypervisor に要求できます。Enclave はこの認証プロセスを使用して、Enclave 固有の測定値を使用して、自身のアイデンティティ(身元)を証明し、外部サービスとの信頼関係を構築することができます。

Enclave の測定値には、Enclave に固有のハッシュ値とプラットフォーム構成レジスタ(PCR)が含まれています。これらは Enclave イメージファイル(EIF)を構築した際、「PCR0」、「PCR1」、「PCR2」というラベルの付いた値で、前のセクションで見たことがあると思います。6つの PCR の完全なリストは次の通りです:

|PCR|Hash of ...|説明|
|--- |--- |--- |
|PCR0|Enclave image file|A contiguous measure of the contents of the image file, without the section data.|
|PCR1|Linux kernel and bootstrap|A contiguous measurement of the kernel and boot ramfs data.|
|PCR2|Application|A contiguous, in-order measurement of the user applications, without the boot ramfs.|
|PCR3|IAM role assigned to the parent instance|A contiguous measurement of the IAM role assigned to the parent instance. Ensures that the attestation process succeeds only when the parent instance has the correct IAM role.|
|PCR4|Instance ID of the parent instance|A contiguous measurement of the ID of the parent instance. Ensures that the attestation process succeeds only when the parent instance has a specific instance ID.|
|PCR8|Enclave image file signing certificate|A measure of the signing certificate specified for the enclave image file. Ensures that the attestation process succeeds only when the enclave was booted from an enclave image file signed by a specific certificate.|

アプリケーションに構成証明を統合できるのに加えて、あらかじめ AWS KMS などのサービスとの統合が用意されているのでそれも利用できます。AWS KMS は Enclave の認証情報を評価することができます。鍵の利用時に条件キーに基づく認証を行うよう `kms:RecipientAttestation:ImageSha384` と `kms:RecipientAttestation:PCR` をキーポリシーとして設定することができます。これらのポリシーを設定すると、Enclave の構成証明ドキュメントが有効であり、指定された条件に合致する場合にのみ、AWS KMS は  KMSの鍵の操作を許可します。
### 機密データ処理のサンプルアプリケーションの概要

{{% notice warning %}}
このモジュールは、Nitro Enclaves 特徴と開発の流れを体験することを目的としています。このモジュールは教材として設計されており、プロダクション環境の Nitro Enclaves アプリケーションアーキテクチャのセキュリティベストプラクティスの例を示すものではありません。
{{% /notice %}}

![Architecture diagram](/images/cryptographic-attestation-arch.png)

このモジュールで作成するアプリケーションは、Nitro Enclave 内で実行されるサーバーコンポーネントと、親インスタンス上で実行されるクライアントコンポーネントで構成されます。クライアントコンポーネントは、データの準備とデータの送信という 2つのフェーズで動作します。

データの準備フェーズでは、アプリケーションのクライアントコンポーネントはクレジットカード番号や社会保障番号などの機密データの値を模した文字列を含む入力ファイルを読み込みます。入力ファイルから機密データをランダムに 1つ選択し、[AWS Key Management Service (KMS)](https://aws.amazon.com/kms/) のカスタマーマスターキー(CMK)を使って暗号化します。送信フェーズではこの暗号化データを利用して処理を行います。

データの送信フェーズでは、クライアントコンポーネントは、事前に準備した暗号データを、安全なローカル vsock チャネルを使用して Enclave 内で実行されるサーバーコンポーネントに渡します。サーバーコンポーネントはこの値を受け取り、vsockと親インスタンス上で実行されているプロキシアプリケーションを介して KMS とのエンド・ツー・エンドの暗号化された接続を行い、暗号化された機密データを復号します。

{{% notice tip %}}
このアプリケーションは Pythonで記述されています。時間があれば、以下のコードを確認してください。 
*~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/cryptographic-attestation*.  
このコードを見て、このサンプルの内部機能を理解してください。親インスタンス上で動作するクライアントコンポーネントは `client.py` ファイルに含まれており、Enclave 内で動作するサーバーコンポーネントは `server.py` ファイルに含まれています。
{{% /notice %}}

{{% notice warning %}}
このセクションでは、サンプルアプリケーションの依存関係をコンパイルし、Enclave 内で実行されるアプリケーションのサーバーコンポーネント用のベース Docker イメージを構築していることを前提としています。まだこのステップを完了していない場合は、[前提条件とセットアップセクション](../getting-started/prerequisites.html#compile-the-dependencies-for-the-nitro-enclaves-workshop-base-image) を実行してください。
{{% /notice %}}

### KMS CMKの作成

まず、アプリケーションで使用する KMS CMKを作成します。

AWS マネージメントコンソールを使用して KMS CMK を作成します:

1. AWS マネジメントコンソールにサインインして、[https://console.aws.amazon.com/kms](https://console.aws.amazon.com/kms) AWS Key Management Service(AWS KMS)コンソールを開きます。

1. AWSリージョンを変更するには、ページの右上にあるリージョンセレクターを使用します。

1. ナビゲーションペインで **カスタマー管理型のキー** を選択します。

1. **キーの作成** を選択します。

1. キータイプとして、**対称** を選択します。

1. **次へ** をクリックします。

1. エイリアスに `my-enclave-key` を入力します。

1. (オプション) CMKの説明を入力します。

1. (オプション) タグキーとタグ値を入力します。複数のタグを追加するには、タグの追加を選択します。

1. **次へ** をクリックします。

1. キーの管理アクセス許可として、キー管理者 (IAM ユーザーまたはロール) は選択しないでください。

1. そのまま **次へ** をクリックします。

1. キーの使用アクセス許可として、暗号化操作できる IAM ユーザーまたはロールは選択しないでください。

    {{% notice info %}}
デフォルトでは、AWSアカウント (rootユーザー) にはフルパーミッションが与えられています。そのため、任意の IAMポリシーで、ユーザーやロールにCMKを使って暗号化操作を行う権限を与えることができます。
    {{% /notice %}}

1. **次へ** をクリックします。

1. 設定を確認してください。設定を修正することも可能です。

1. **完了 **をクリックし、CMKを作成します。

### KMSキーポリシーの設定

作成した KMS のキーポリシーには、IAMユーザーやロールが IAMポリシー文書を介してキーへのアクセスを許可するステートメントが含まれています。このポリシーは以下のようになります
<pre>
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111122223333:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        }
    ]
</pre>

ワークショップの Cloud9 環境に関連付けられた IAM プリンシパルは、CMK に対するアクションの権限を与えられていません。たとえば、Cloud9 のターミナルから以下のコマンドを実行してキーに関する情報を表示しようとしても、拒否されます:
```sh
$ aws kms describe-key --key-id "alias/my-enclave-key"
```

{{% notice tip %}}
このリクエストの拒否は、ワークショップの Cloud9 環境に関連付けられた IAMプリンシパルが、AWS マネジメントコンソールへのサインインに使用された IAMプリンシパルと同じではなく、CMK に対するアクションの権限を持っていないことを示しています。KMS へのアクセス管理の詳細については、[Authentication and access control for AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/control-access.html) を参照してください。
{{% /notice %}}

Cloud9 環境で鍵を使ってデータを暗号化・復号できるようにするために、KMS キーポリシーで許可する権限を設定します。

CMK の新しいキーポリシーを設定します:

1. Cloud9 のターミナルで以下のコマンドを実行して、Cloud9 の環境に関連付けられた AWS IAM のプリンシパルとアカウントの情報を環境変数に格納します:
    ```sh
    $ export AWS_PRINCIPAL=`aws sts get-caller-identity | jq -r ".Arn"`
    $ export ACCOUNT_ID=`aws sts get-caller-identity | jq -r ".Account"`
    ```

1. Cloud9 のターミナルで以下のコマンドを実行して、事前に用意されたキーポリシーのテンプレートに先ほどの情報を追加します:
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/cryptographic-attestation
    $ sed -e "s|ACCOUNT_ID|${ACCOUNT_ID}|" -e "s|AWS_PRINCIPAL|${AWS_PRINCIPAL}|" key_policy_template.json > key_policy.json
    ```

#### CMK のキーポリシーを更新する:

1. AWS Key Management Service (AWS KMS) のコンソール [https://console.aws.amazon.com/kms](https://console.aws.amazon.com/kms)を開きます。

1. AWSリージョンを変更するには、ページ右上にあるリージョンセレクターを使います。

1. ナビゲーションペインで「**カスタマー管理型のキー**」を選択し、アカウント内の鍵を表示します。

1. CMK のリストから、 **my-enclave-key** を選択します。

1. **キーポリシー** タブを選択します。

1. **キーポリシー** タブは *デフォルトビュー* 形式で表示されています。キーポリシーのドキュメントを表示するために **ポリシービューへの切り替え** を選択します。

    *ポリシービュー* が表示されます。キー ポリシーには、CMK へのアクセスが許可されたプリンシパルと、そのプリンシパルが実行できるアクションが表示されています。

1. 別のウィンドウで、Cloud9 のターミナルに戻り`ls`コマンドを実行します。出力されたリストから **key_policy.json** をマウスカーソルでクリックします。

1. **Open** をクリックします。

1. 新しいキーポリシーの内容が Cloud9 のエディタータブで開かれます。ウィンドウ内のテキストをすべて選択して、クリップボードにコピーしてください。

1. KMS CMKのウィンドウに戻ります。**キーポリシー** タブが開いている状態で **編集**をクリックします。

1. キーポリシー全体を削除し、先ほどコピーした新しいキーポリシーを貼り付けて、**変更を保存** をクリックします。

### Enclave の構築、実行、デバッグモードでの接続

1. Cloud 9 で新しいターミナル・セッションを開始します。(新規ターミナルセッションを開始するには、メニューバーの **Window** / **New Terminal** を選択します。)

1. Cloud9 のターミナルで以下のコマンドを実行して、Enclave アプリケーションの Docker コンテナをビルドします:
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/cryptographic-attestation
    $ docker build ./ -t "data-processing"
    ```

1. 以下のコマンドを実行して、Enclave イメージファイルをビルドします:
    ```sh
    $ nitro-cli build-enclave --docker-uri "data-processing:latest" --output-file "data-processing.eif"
    ```

    **出力** は以下のようになります:
    <pre>
    Enclave Image successfully created.
    {
    "Measurements": {
        "HashAlgorithm": "Sha384 { ... }",
        "PCR0": "287b24930a9f0fe14b01a71ecdc00d8be8fad90f9834d547158854b8279c74095c43f8d7f047714e98deb7903f20e3dd",
        "PCR1": "aca6e62ffbf5f7deccac452d7f8cee1b94048faf62afc16c8ab68c9fed8c38010c73a669f9a36e596032f0b973d21895",
        "PCR2": "0315f483ae1220b5e023d8c80ff1e135edcca277e70860c31f3003b36e3b2aaec5d043c9ce3a679e3bbd5b3b93b61d6f"
    }
    }
    </pre>

    {{% notice info %}}
`nitro-cli build-enclave` コマンドの出力は、Enclave イメージファイルの固有の測定値です。この出力は上の例と同じではありません。これらの測定値はこのセクションでは重要なので、後で参照できるように保存しておいてください。
    {{% /notice %}}


1. Cloud9 のターミナルで以下のコマンドを実行して、Enclave アプリケーションを起動します:
    ```sh
    $ nitro-cli run-enclave --debug-mode --cpu-count 2 --memory 2500 --eif-path "./data-processing.eif"
    ```

1. 次のコマンドを発行して、Enclave のコンソールに接続します:
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli console --enclave-id ${ENCLAVE_ID}
    ```

    このターミナルタブには、実行中の Enclave のデバッグモードのコンソール出力が表示されます。

### Enclave アプリケーションとのやりとり

1. 元の Cloud9 ターミナルタブに戻り、以下のコマンドを実行して依存関係をインストールします。
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/cryptographic-attestation
    $ pip3 install --user -r "requirements.txt"
    ```

1. 以下のコマンドを実行します。このコマンドは、`values.txt` から機密データを１つランダムに選択し、KMS CMK を使って暗号化します。
    ```sh
    $ python3 client.py --prepare --values "values.txt"  --alias "my-enclave-key"
    ```

    このコマンドが成功すると、選択された機密データの下 4桁の文字列と、暗号化された文字列を画面に表示します。また、暗号文を格納した新しいファイル `string.encrypted` が作成されます。

1. この暗号文が含まれたファイルを、次のコマンドを実行して Enclave に送信します。
    ```sh
    $ python3 client.py --submit --ciphertext "string.encrypted"  --alias "my-enclave-key"
    ```

    機密データの下4桁の文字列が親インスタンスに返されて、ターミナルで表示されているのがわかります。

### 構成証明の活用

アプリケーションの大まかな構成ができたので、次の段階に進みます。現在構成されているアプリケーションは、機密データの処理を分離するために、特に改善すべき2つの領域があります。親インスタンスは現在、平文の機密データを見ることができますが、それには a.) Enclave のデバッグコンソールを見ることと、b.) KMS CMK を使って値自体を復号することが必要です。

デバッグコンソールに接続した Cloud9 の別ターミナルに移動します。Enclave 内で実行されているプロセスに関する情報が表示されます。その中には、Enclave に暗号文の形で送信した機密データの値の平文全体も含まれています。

この値をコンソールに出力しないように enclave アプリケーションを修正することができます。ただしそれでも、親インスタンスは KMS を直接使用してこの値を復号することができます。`string.encrypted`の暗号文を復号するには、先ほどのCloud9 のターミナルに戻り、以下のコマンドを実行します。

```sh
$ base64 -di string.encrypted > string.encrypted.binary &&
  aws kms decrypt \
  --ciphertext-blob "fileb://string.encrypted.binary" \
  --output "text" \
  --query "Plaintext" | base64 --decode
```

このコマンドは、機密データの完全な平文をコンソールに表示することがわかります。このコマンドは、Cloud9 環境のクレデンシャルを使用して KMS を直接呼び出しています。Enclave 内で実行されているサーバーコンポーネントには全く依存していません。

しかし、AWS Nitro Enclaves の構成証明(身元証明)と AWS KMS と利用することで、親インスタンスが機密データを復号できず、Enclave は復号できるようにアプリケーションを構成することができます。さらに、構成証明により、親インスタンスのユーザーが Enclave のデバッグコンソールを介して機密データにアクセスすることを禁止することができます。

この例では PCR0 を使用します。PCR0 は`data-processing.eif`ファイルの測定値のユニークなハッシュです。

認証条件をキーポリシーに追加します:

1. Cloud9 のエディターで key_policy.json を開きます。

1. 30行目の最後までカーソルを移動します (`"Resource": "*"`と記載された行です)

1. `,` を入力します。

1. キーボードのリターンキーを押して、新しい行に移動します。

1. 以下のテキストをコピーして、Cloud9 のエディターに貼り付けます。

    <!-- Please don't change indentation on JSON block below since we are making it neatly copy-pasteable. -->
    ```
    "Condition": {
                  "StringEqualsIgnoreCase": {
                      "kms:RecipientAttestation:PCR0": "EXAMPLEbc2ecbb68ed99a13d7122abfc0666b926a79d5379bc58b9445c84217f59cfdd36c08b2c79552928702EXAMPLE"
                  }
              }
    ```

1. PCR0 の値 (*EXAMPLEbc2ecbb68ed99a13d7122abfc0666b926a79d5379bc58b9445c84217f59cfdd36c08b2c79552928702EXAMPLE*) を、Enclave のビルド時に表示された PCR0 の値に置き換えます。

    {{% notice tip %}}
PCR0 の値をメモしてなかった場合は、Enclave を再構築することでこの値を再び確認できます。
    {{% /notice %}}

キーポリシーを更新します:

* 上記の[update the key policy for your CMK](#update-the-key-policy-for-your-cmk)の手順に従ってください

キーポリシーでは、Cloud9 環境のプリンシパルが CMK を使用して暗号化することを許可していますが、復号は Enclave 内でのみ取得可能な署名入り構成証明ドキュメントが要求に添付された場合に限り許可しています。

### Enclave 構成証明ベースの KMS キーポリシーの検証

キーポリシーの更新が完了したら、Cloud9 のターミナルで先程のコマンドを実行して、新しい条件が有効になったことを確認します。
```sh
$ base64 -di string.encrypted > string.encrypted.binary &&
  aws kms decrypt \
  --ciphertext-blob "fileb://string.encrypted.binary" \
  --output "text" \
  --query "Plaintext" | base64 --decode    
```

正しくポリシーが設定されていると `AccessDeniedException` のメッセージが表示されます。これは、Cloud9 環境のプリンシパルがキーを使って復号する権限に、特定の エンクレイブ・イメージ・ファイル(`data-processing.eif`) で起動された Enclave 内からのリクエストにのみ適用するという条件を付けているためです。

この変更は、デバッグモードでの Enclave の動作にも影響します。Cloud9 のターミナルで以下のコマンドを実行して、暗号化された値を Enclave に再送信して動作確認してください。
```sh
$ python3 client.py --submit --ciphertext "string.encrypted"  --alias "my-enclave-key"
```

Nitro Hypervisorは、デバッグモードで起動した Enclave には実際の PCR 値で構成証明ドキュメントを署名しないため、このコマンドは失敗します。

{{% notice note %}}
デバッグモードで起動した Enclave は、PCR がすべてゼロで構成された構成証明ドキュメントが生成されます (`0000000000000000`) このドキュメントは、 暗号技術を用いた構成証明(身元証明)には使用できません。
{{% /notice %}}

プロダクションモードで起動したときに、Enclave が正しく復号できることを確認します:

1. Cloud9 のターミナルで次のコマンドを発行して、Enclave を終了します:
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
    ```

1. Cloud9 のターミナルで次のコマンドを発行して、Enclave をプロダクションモードで起動します:
    ```sh
    $ nitro-cli run-enclave --cpu-count 2 --memory 2500 --eif-path "./data-processing.eif"
    ```

1. 別の Cloud9 ターミナルウィンドウで次のコマンドを発行して、暗号化された値をエンクレーブに送信します:
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/cryptographic-attestation
    $ python3 client.py --submit --ciphertext "string.encrypted"  --alias "my-enclave-key"
    ```

1. 機密データの値の下4桁がコンソールに表示されることを確認します。

暗号技術を用いた構成証明(身元証明)と KMS 条件キーを追加したことにより、親インスタンス上のユーザーやプロセスは、KMS を使って値を直接復号することも、デバッグコンソールで表示することもできず、復号された平文の値にアクセスできなくなりました。その一方プロダクションモードで実行した Enclave は KMS を使用して機密データを復号することができ、最後の4桁だけを親インスタンスに返します。

### Enclave のアプリケーションコードの変更

ここまでは、機密データを処理するアプリケーションの基本的な機能と、親インスタンスが自身のクレデンシャルを使用して復号したり、デバッグコンソールを介して平文の機密データにアクセスすることを防ぐために、構成証明をどのように使用できるかについて説明してきました。しかし、やる気のある攻撃者が、 Enclave のアプリケーションコードを変更して、vsock経由で平文の値を返すように修正するとどうでしょうか。何が起こるか見てみましょう。

Enclave のアプリケーションファイル `server.py` には，次のようなコードが含まれています:

```python {linenos=true, linenostart=77}
    last_four = str(plaintext)[-4:]
    r["last_four"] = last_four

c.send(str.encode(json.dumps(r)))

c.close()
```

`server.py` の 77 行目にある末尾の `[-4:]` で、プログラムが平文の最後の 4 つの数字だけを返しています。このコードを修正して、平文全体を vsock 経由で親インスタンスに返すように修正するには、Cloud9 のターミナルで以下のコマンドを実行します。

```sh
$ sed -i "s|\[-4:\]||" ./server.py
```

このコマンドを実行すると、`server.py`は次のようになります。

```python {linenos=true, hl_lines=[1] linenostart=77}
    last_four = str(plaintext)
    r["last_four"] = last_four

c.send(str.encode(json.dumps(r)))

c.close()
```

この修正したコードを Enclave で実行するには、新しいdockerイメージとEIFをビルドする必要があります:

1. Cloud9 のターミナルで以下のコマンドを実行して、修正したコードで新しい docker イメージをビルドします。
    ```sh
    $ docker build ./ -t "data-processing-modified"
    ```

1. Cloud9 のターミナルで以下のコマンドを実行して、作成した dockerイメージから EIF ファイルをビルドします。
    ```sh
    $ nitro-cli build-enclave --docker-uri "data-processing-modified:latest" --output-file "data-processing-modified.eif"
    ```

    {{% notice info %}}
ターミナルウィンドウに表示された測定値を注意深く確認します。最初に`data-processing.eif`ファイルをビルドした時の測定値と比較すると、アプリケーションコードやイメージファイル全体が変更されているため、PCR0 と PCR2 は異なる値を示していることがわかります。PCR1 は、変更されていないカーネルと boot ramfs のデータの測定値を反映しているので、同じ値になっています。
    {{% /notice %}}

1. Cloud9 のターミナルで次のコマンドを実行して、実行中の Enclave を終了します。
    ```sh
    $ ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
    ```


1. Cloud9 のターミナルで以下のコマンドを実行して、先ほどビルドしたEIFで新しい Enclave を起動します。
    ```sh
    $ nitro-cli run-enclave --cpu-count 2 --memory 2500 --eif-path "./data-processing-modified.eif"
    ```

1. Cloud9 のターミナルで次のコマンドを実行して、暗号文を Enclave に送信します。先ほど修正したように、Enclave は提供された暗号文を復号して平文全体を返すはずです:
    ```sh
    $ python3 client.py --submit --ciphertext "string.encrypted" --alias "my-enclave-key"
    ```

このアプリケーションのセキュリティモデルは、依然として機密データを保護しています！　Enclave 内の `server.py` プログラムが平文全体を返すように修正された後も、親インスタンスに平文を返すことができませんでした。修正されたプログラムが平文の値を返せないのは、構成証明によって復号できなかったからです。プログラムを変更してEIFを再構築すると、新しい PCR0 値が生成されました。Enclave 内のプログラムが `KMS:Decrypt` を呼び出したところ、提供された署名付き構成証明ドキュメントの PCR0 の値と、KMS が復号許可を出すように設定した承認済み EIF の PCR0 が一致していなかったため、拒否されました。

### まとめ

このセクションでは、Enclave 内で暗号化された値を処理するサンプルアプリケーションをビルト、デプロイ、およびテストしました。次に、信頼された Enclave アプリケーションの外部で平文が取得される機会を特定しました。そして、Nitro Enclaves の暗号技術を用いた構成証明(身元証明)と AWS KMS のキー条件を使って、機密データを処理するアプリケーションの隔離と機密性を向上させることができました。

---
#### Workshop を続けるには、[トラブルシューティング](troubleshooting.html)のセクションに進んでください。
