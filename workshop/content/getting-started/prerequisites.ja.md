---
title: "前提条件と環境のセットアップ"
weight: 30
---


プロセスを効率化するために、開発環境として AWS Cloud9 IDE を使用することになります。Cloud9 IDE で _Nitro Enclaves Workshop_ を開いて、Workshop で使用する前提条件をインストールします。これらの前提条件には下記が含まれます:

* [AWS 管理の一時的な認証情報の無効化](#disable-aws-managed-temporary-credentials)
* [Nitro Enclaves CLI とツールのインストールとセットアップ](#install-and-configure-nitro-enclaves-cli-and-tools)
* [Workshop リポジトリのクローン](#clone-the-workshop-repository)
* [Nitro Enclaves Workshop ベースイメージ用の依存関係のコンパイル](#compile-the-dependencies-for-the-nitro-enclaves-workshop-base-image)

### AWS 管理の一時的な認証情報の無効化

1. AWS Cloud9 IDE で AWS Cloud9 環境を起動し、メニューバーから **AWS Cloud9 icon / Preferences** を選択
![Choose preferences](/images/prerequisites-1-choose-preferences.png?featherlight=false)

1. ナビゲーションパネルの **Preferences** タブで最下部までスクロールし **AWS Settings / Credentials** を選択
![Choose AWS settings credentials](/images/prerequisites-2-choose-aws-settings-credentials.png?featherlight=false)

1. **AWS managed temporary credentials** をトグルさせて AWS managed temporary credentials をオフに設定
![Toggle AWS managed temporary credentials](/images/prerequisites-3-toggle-aws-managed-temporary-credentials.png?featherlight=false)

### Nitro Enclaves CLI とツールのインストールとセットアップ
{{% notice note %}}
Workshop の中で使用するコマンドの多くは、AWS Cloud9 IDE の中のターミナルセッションで実行します。新規のターミナルセッションを開始するには、メニューバーの **Window** / **New Terminal** を選択します。
{{% /notice %}}

1. Nitro Enclaves CLI をインストールし enclaves を実行できるようにします
    ```sh
    $ sudo amazon-linux-extras install aws-nitro-enclaves-cli -y
    ```

1. Nitro Enclaves 開発ツールをインストールします。enclaves をビルドできるようになります
    ```sh
    $ sudo yum install aws-nitro-enclaves-cli-devel -y
    ```

1. パーミッションを設定します
    ```sh
    $ sudo usermod -aG ne $USER
    $ sudo usermod -aG docker $USER
    ```

1. Nitro Enclaves CLI が正しくインストールできたかどうかを確認します
    ```sh
    $ nitro-cli --version
    ```
    **出力結果** は以下のようになるはずです
    <pre>Nitro CLI &lt;VERSION&gt;</pre>

1. Nitro Enclaves allocator サービスを起動し有効化します
    ```sh
    $ sudo systemctl start nitro-enclaves-allocator.service && sudo systemctl enable nitro-enclaves-allocator.service
    ```

1. Docker サービスを起動し有効化します
    ```sh
    $ sudo systemctl start docker && sudo systemctl enable docker
    ```

1. インスタンスを再起動します。この時点において、group に user を追加した `usermod` コマンドが有効になるように、ログアウトしてログインし直す必要があります。1つの方法は `exec sudo su --login $USER` のようにして新しいシェルを起動することであり、もう 1つの方法は現在のシェルのログイン前に `groupadd` と `usermod` コマンドを準備することです。しかしながら、Cloud9 は再起動を正しく処理しシェルを同様の状態にすることができるので、インスタンスを再起動することにします。
    ```sh
    $ sudo shutdown -r now
    ```
    再起動完了にそれほど時間はかかりません(30秒程度)
    
    <!--
        {{% notice note %}}
    group に `ec2-user` user を追加する `usermod` コマンドを確実に実行するためには、ログアウトして再度ログインするだけでよいのですが、Cloud9 は正しく再起動を処理し、シェルを同様の状態に戻せます。別の方法として `exec sudo su --login $USER` のように新しいシェルを起動することも可能でます。
        {{% /notice %}}
    -->

1. `ec2-user` user が `docker` と `ne` の両方の group のメンバーになっていることを確認します。
    ```sh
    $ id $USER
    ```

    **出力結果** は以下のようになるはずです
    <pre>uid=1000(ec2-user) gid=1000(ec2-user) groups=1000(ec2-user),4(adm),10(wheel),190(systemd-journal),991(docker),1001(ne)</pre>

{{% notice tip %}}
詳細情報は、[公式ドキュメント](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave-cli-install.html) を確認してください。
{{% /notice %}}

### Clone the workshop repository

1. Workshop のリポジトリをダウンロードするために `git clone` コマンドを使用します。このリポジトリは、後のモジュールで使用するコンテンツを含んでいます。
    ```sh
    $ git clone --depth 1 https://github.com/aws-samples/aws-nitro-enclaves-workshop.git
    ```

{{% notice note %}}
[はじめての Enclave](../my-first-enclave.html) の [暗号技術を用いた身元証明(構成証明)](../my-first-enclave/cryptographic-attestation.html) セクションを実施する予定であれば、以下のステップを完了させる必要があります。このセクションを実施しないのであれば、[はじめての Enclave](../my-first-enclave.html) モジュールに進めます。
{{% /notice %}}

### Nitro Enclaves Workshop ベースイメージ用の依存関係のコンパイル

Nitro Enclavesでは、Enclaves で起動したいアプリケーションをパッケージ化するための便利なフォーマットとして、docker イメージを使用します。この Workshop のサンプルの中には、コンパイルしなければならない依存関係が必要なアプリケーションがあります。

ベースとなる docker イメージ用にこれらの依存関係をパッケージするために:

1. 新規のターミナルセッションを開始します (新規のターミナルセッションを開始するには、メニューバーの **Window** / **New Terminal** を選択します)

1. 下記のコマンドを実行してMy First Enclave モジュール用のコードのディレクトリに移動します:
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/getting-started
    ```

1. 下記のコマンドを実行してビルドプロセスを開始します:
    ```sh
    $ docker build ./ -t "enclave_base"
    ```

{{% notice tip %}}
ビルドプロセスの実行中に赤い文字が出力されますが、問題はありません。`docker build` のプロセスが完了するまでに最大で 15分程度かかりますので、ビルド中も Workshop を進める必要があります。そのためには、使用しているターミナルセッションを開いたままで、Cloud9 IDE で以前使用していたターミナルセッションに戻ってください。
{{% /notice %}}

---
#### [はじめての Enclave](../my-first-enclave.html) モジュールに進んでください
