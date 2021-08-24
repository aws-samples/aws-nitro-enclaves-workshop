---
title: "Cloud9 環境の作成"
chapter: false
weight: 2
---

{{% notice note %}}
前述の [AWS アカウントの作成](account.html) で作成したユーザーでログインした状態で、以下の手順を進めてください。
{{% /notice %}}
{{% notice warning %}}
新規アカウントの作成をスキップし既存のアカウントを使用する場合は、使用するアカウントにデフォルトVPC があることを確認してください。デフォルトVPC がない場合は、次の手順 [デフォルトVPC の作成](https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html#create-default-vpc)を実施し作成してください。
{{% /notice %}}

1. AWS CloudFormation のテンプレートをこの Workshop の GitHub レポジトリからダウンロードします。
    ```sh
    curl https://raw.githubusercontent.com/aws-samples/aws-nitro-enclaves-workshop/main/resources/templates/cloud9.yaml -o cloud9.yaml
    ```

1. 新規のスタックを作成するために AWS CloudFormation コンソールに移動します。

    https://console.aws.amazon.com/cloudformation/home#/stacks/create/template

1. 前の手順でダウンロードした CloudFormation テンプレートを指定しアップロードします。その後 _次へ_ をクリックします。
![テンプレートを指定](/images/cloud9-1-specify-template.png?featherlight=false)

1. スタックを `NitroEnclavesWorkshop` と命名します。必要に応じて、EBSボリュームサイズをデフォルトの値から増やしても良いです。_次へ_ をクリックします。
![スタックの詳細を指定します](/images/cloud9-2-specify-stack-details.png?featherlight=false)

1. スタックオプションはそのままにして _次へ_ をクリックします。
![スタックオプションを設定する](/images/cloud9-3-configure-stack-options.png?featherlight=false)

1. 3つ全てのチェックボックスを選択し、_スタックの作成_ をクリックします。
{{% notice warning %}}
この CloudFormation スタックは AWSリソースを作成しますので、これらのリソースが AWSアカウントに残っていると追加料金が発生する場合があります。 
Workshop のクリーンアップ手順を参照して、作成された全てのリソースを確認してください。
{{% /notice %}}
![Review](/images/cloud9-4-review.png?featherlight=false)

1. スタックが作成され `CREATE_COMPLETE` の状態になるまでの時間は気分転換に最適です。おおよそ 5分程度かかります。

1. IDE 環境を確認し起動するために AWS Cloud9 コンソールへ移動します

    https://console.aws.amazon.com/cloud9/home

1. Cloud9 IDE 環境を新規のタブで開きます
![Cloud9 環境を開く](/images/cloud9-5-environment.png?featherlight=false)

---
#### Workshop の次のセクション [前提条件と環境のセットアップ](../prerequisites.html) に進む
