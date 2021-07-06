---
title: "Como criar uma conta da AWS"
chapter: false
weight: 1
---

{{% notice warning %}}
Sua conta deve ter a capacidade de criar novas funções do IAM e escopo outras permissões do IAM.
{{% /notice %}}

1. Se você ainda não tiver uma conta da AWS com acesso de administrador:[criar uma agora clicando aqui](https://aws.amazon.com/getting-started/)

1. Depois de ter uma conta da AWS, verifique se você está seguindo as etapas restantes do workshop como um usuário do IAM com acesso de administrador à conta da AWS:
[Criar um novo usuário do IAM para usar no workshop](https://console.aws.amazon.com/iam/home?#/users$new)

1. Insira os detalhes do usuário:
![Criar usuário](/images/iam-1-create-user.png?featherlight=false)

1. Anexe a política do IAM entitulada AdministratorAccess :
![Anexar política](/images/iam-2-attach-policy.png?featherlight=false)

1. Clique para criar o novo usuário:
![Confirmar Usuário](/images/iam-3-create-user.png?featherlight=false)

1. Tome nota do URL de login e salve:
![URL de login](/images/iam-4-save-url.png?featherlight=false)

---
#### Proceed to the [Create a Cloud9 environment](cloud9.html) section to continue the workshop.