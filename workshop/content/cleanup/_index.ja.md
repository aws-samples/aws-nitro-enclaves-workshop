---
linkTitle: "後片付け"
title: "Workshop Cleanup"
weight: 30
chapter: true
---


<!-- TODO: Temporarily fixing duplicate headers in chapters on published workshop. Note: This hides header from local build.
# Workshop 後片付け
-->

### AWS Nitro Enclaves Workshop に参加いただきありがとうございました!
---

これでモジュールを完了しましたので、作成した全てのリソースを削除する手続きに進めます。

## ...AWS イベントで

お片付け作業は不要で、残りは AWS 側で処理します。


## ...あなた自身の

### AWS Cloud9

すべての作業は、enclave のホストとしても機能する Cloud9 IDE に限定されていました。従いまして、環境をお片付けするには CloudFormation スタックを削除する必要があります:

1. 新規のスタックを作成するための AWS CloudFormation コンソールに移動します。

    https://console.aws.amazon.com/cloudformation/home#/stacks/stackinfo

1. Workshop を始める時に作成した `NitroEnclavesWorkshop` スタックを選択し、_削除_ をクリックします。_スタックの削除_ をクリックして削除することを再確認します。
{{% notice warning %}}
Cloud9 環境の中の全てのファイルが削除されます。もし何か保存しておきたいファイルがある場合は、スタックを削除するまえに保存しておいてください。
{{% /notice %}}
![Stack deletion](/images/cleanup-1.png?featherlight=false)
{{% notice info %}}
5分程度でスタックの削除が完了します。`aws-cloud9-*` で始まる他のスタックも削除されます。
{{% /notice %}}
それに加えて、CloudFormation テンプレートから自動的に作成されたサービスロール(`AWSCloud9SSMAccessRole`)と IAM インスタンスプロファイル(`AWSCloud9SSMInstanceProfile`)の双方が削除されます。これらの IAM リソースは、AWS アカウントにそのまま残しておいても費用は発生しません。
{{% notice note %}}
今後、インスタンスにアクセスする際にシステムマネージャを使用しない場合は、サービスロール `AWSCloud9SSMAccessRole` も削除できます。詳細情報は、_IAM User Guide_ の [ロールまたはインスタンスプロファイルの削除](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_manage_delete.html) を確認してください。
{{% /notice %}}
IAM リソースに関する詳細は [公式ドキュメント](https://docs.aws.amazon.com/cloud9/latest/user-guide/ec2-ssm.html#service-role-ssm) を確認してください。

### AWS Key Management Service (KMS)

Workshop の一部として、KMS Customer Managed Key (CMK) を使用してデータを暗号化し複合しました。KMS コンソールで直接キーを削除したいのではないかと予想します。

AWS Management Console を使用して KMS CMK を削除します:

1. AWS Management Console にログインして AWS Key Management Service (AWS KMS) コンソール [https://console.aws.amazon.com/kms](https://console.aws.amazon.com/kms) を開きます。

1. リージョンを変更するには、ページ右上のリージョンセレクタでリージョンを選択します。

1. ナビゲーションペインで **カスタマー管理型のキー** を選択します。

1. Workshop で使用した `my-enclave-key` を選択します。

1. **キーのアクション** **キーの削除をスケジュール** を選択します。

1. (オプション) 待機期間を最小の 7日間に減らします。

1. **削除するキー** テーブルには Workshop で使用した `my-enclave-key` のみが記載されていることを確認します。

1. ** X 日の待機期間後にこれらのキーの削除をスケジュールすることを確認します。** を選択します。

1. **削除をスケジュール** を選択します。

---
### AWS Nitro Enclaves Workshop に参加いただきありがとうございました!
