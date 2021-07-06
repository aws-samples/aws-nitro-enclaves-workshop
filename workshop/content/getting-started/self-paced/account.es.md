---
title: "Crea una cuenta de AWS"
chapter: false
weight: 1
---

{{% notice warning %}}
Tu cuenta debe poder crear nuevos roles de IAM y otras funcionalidades.
{{% /notice %}}

1. Si aún no tienes una cuenta de AWS con acceso de administrador, [crea una dando clic aquí](https://aws.amazon.com/getting-started/)

1. Una vez tengas tu cuenta de AWS, asegúrate de seguir estos pasos del workshop como usuario IAM y no como usuario raiz (root). Si no sabes cómo crear un usuario IAM, puedes seguir [estos pasos](https://console.aws.amazon.com/iam/home?#/users$new)

1. Ingresa los datos del usuario:
![Create User](/images/iam-1-create-user.png?featherlight=false)

1. Adjúntale la política llamada "AdministratorAccess":
![Attach Policy](/images/iam-2-attach-policy.png?featherlight=false)

1. Da clic para crear el nuevo usuario:
![Confirm User](/images/iam-3-create-user.png?featherlight=false)

1. Toma nota de la URL de inicio de sesión:
![Login URL](/images/iam-4-save-url.png?featherlight=false)

---
#### Proceed to the [Create a Cloud9 environment](cloud9.html) section to continue the workshop.