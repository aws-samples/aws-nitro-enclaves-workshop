---
title: "AWS アカウントの作成"
chapter: false
weight: 1
---

{{% notice warning %}}
あなたの AWS アカウントでは、新規の IAM ロールを作成し他の IAM パーミッションを参照する権限が必要です。
{{% /notice %}}

1. もし、あなたが管理者権限を持つ AWS アカウントを持っていない場合は: [ここをクリック
して作成してください](https://aws.amazon.com/getting-started/)

1. AWS アカウントがある場合は、管理者権限を持つ IAM ユーザでアクセスし残りの Workshop の手順に従ってください:
[Workshop 用に新規の IAM ユーザを作成する](https://console.aws.amazon.com/iam/home?#/users$new)

1. ユーザの詳細を入力:
![ユーザの作成](/images/iam-1-create-user.png?featherlight=false)

1. AdministratorAccess IAM ポリシーをアタッチする:
![Attach Policy](/images/iam-2-attach-policy.png?featherlight=false)

1. 新規ユーザを作成するためにユーザーの作成をクリック:
![Confirm User](/images/iam-3-create-user.png?featherlight=false)

1. ログイン URL をメモして保存:
![Login URL](/images/iam-4-save-url.png?featherlight=false)

---
#### Workshop の次のセクション [Cloud9 環境の作成](cloud9.html) に進む
