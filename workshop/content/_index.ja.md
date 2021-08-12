---
title: "AWS Nitro Enclaves Workshop"
chapter: true
weight: 1
---

<!-- TODO: Temporarily fixing duplicate headers in chapters on published workshop. Note: This hides the header from the local build.
# AWS Nitro Enclaves Workshop
-->

![AWS Nitro Enclaves Splash Image](/images/nitro-enclaves.png?featherlight=false)

_機密性の高いデータを AWS Nitro Enclaves で処理する方法を学習します_
## What is AWS Nitro Enclaves?

AWS Nitro Enclaves は、お客様が分離されたコンピュート環境を構築することにより、Amazon EC2インスタンス内の個人を特定できる情報(PII)、ヘルスケア、金融、知的財産データなどの機密性の高いデータを更に保護し、安全な処理を実現します。Nitro Enclaves は、EC2インスタンスの CPU とメモリの分離を提供するのと同じ Nitro Hypervisor 技術を使用しています。

Nitro Enclaves は、最も機密性の高いデータ処理アプリケーションにおける攻撃対象エリアを削減するのに役立ちます。Enclaves はセキュリティクリティカルなアプリケーションをホストするための、隔離され、強化され、高度に制約された環境を提供します。Enclaves には永続的なストレージ、インタラクティブなアクセス、外部ネットワーク環境はありません。インスタンスと Enclaves の間の通信は、セキュアなローカルチャネルが使用されます。デフォルトでは、インスタンスの root ユーザーや admin ユーザーであっても、Enclaves 内部にアクセスしたり SSH接続できません。認証済のコードのみが実行されていることを確認できるよう Nitro Enclaves にはソフトウェアの暗号認証機能があり、AWS Key Management Service と統合されているために Enclaves のみが機密情報にアクセスできるようになります。

[Official Documentation](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html)

{{% notice warning %}}
この Workshop では AWS リソースが作成され、これらのリソースが AWS アカウントに残ったままだと追加料金が発生する場合があります。 
Workshop のクリーンアップ手順  <!--in each section--> を参照して、作成されたリソースをすべて確認してください<!-- by automated stacks-->。
{{% /notice %}}

---
#### [開始方法](getting-started.html) のモジュールに進んでください。
