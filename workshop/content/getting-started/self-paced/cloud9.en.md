---
title: "Create a Cloud9 environment"
chapter: false
weight: 2
---

{{% notice note %}}
Follow the steps below while logged in to you account with the user your created in the previous [Create an AWS account](account.html) section.
{{% /notice %}}
{{% notice warning %}}
If you skipped creation of a new account and use existing account, make sure it has default vpc. If it is missing you can follow next steps to [Create a Default VPC](https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html#create-default-vpc).
{{% /notice %}}

1. Download the AWS CloudFormation template from this workshop's GitHub repo.
    ```sh
    curl https://github.com/aws-samples/aws-nitro-enclaves-workshop/raw/main/resources/templates/cloud9.yaml -o cloud9.yaml
    ```

1. Navigate to the AWS CloudFormation console to create a new stack.

    https://console.aws.amazon.com/cloudformation/home#/stacks/create/template

1. Select and upload the CloudFormation template that was downloaded previously. Then click _Next_.
![Specify template](/images/cloud9-1-specify-template.png?featherlight=false)

1. Name your stack `NitroEnclavesWorkshop` and, if you'd like, increase the volume size beyond the default value. Then click _Next_.
![Specify stack details](/images/cloud9-2-specify-stack-details.png?featherlight=false)

1. Leave the stack options as-is and proceed to the next step by clicking _Next_.
![Configure stack options](/images/cloud9-3-configure-stack-options.png?featherlight=false)

1. Select all three capabilities and click _Create stack_.
{{% notice warning %}}
This CloudFormation stack will create AWS resources and you may incur additional charges if these resources are left in your AWS account.  
Please refer to cleanup procedures of the workshop and review all the resources created.
{{% /notice %}}
![Review](/images/cloud9-4-review.png?featherlight=false)

1. This is a good time to stretch your legs, while the stack is created and reaches `CREATE_COMPLETE`. This takes about 5 minutes.

1. Navigate to the AWS Cloud9 console to view and open your environment IDE.

    https://console.aws.amazon.com/cloud9/home

1. Open your Cloud9 environment IDE in a new tab.
![Open Cloud9 enviroment](/images/cloud9-5-environment.png?featherlight=false)

---
#### Proceed to the [Prerequisites and environment setup](../prerequisites.html) section to continue the workshop.