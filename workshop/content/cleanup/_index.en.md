+++
linkTitle = "Cleanup"
title = "Workshop Cleanup"
weight = 200
chapter = true
+++


<!-- TODO: Temporarily fixing duplicate headers in chapters on published workshop. Note: This hides header from local build.
# Workshop Cleanup
-->

### Thank you for exploring the AWS Nitro Enclaves workshop!
---

Now that you have completed the module(s), we can proceed to destroy all of the resources that were created. To begin cleanup, if you completed the workshop...

## ...on your own

### AWS Cloud9

All the work was limited to the Cloud9 IDE which also doubled as our enclaves host. Therefore, to clean up the environment, you must deleted the CloudFormation stack:

1. Navigate to the AWS CloudFormation console to create a new stack.

    https://console.aws.amazon.com/cloudformation/home#/stacks/stackinfo

1. Select the `NitroEnclavesWorkshop` stack that you created at the beginning of the workshop and click _Delete_. You will then confirm by clicking _Delete stack_.
{{% notice warning %}}
All files in the Cloud9 environment will be destroyed. If you'd like to save any files, please do so before you proceed with the stack deletion.
{{% /notice %}}
![Stack deletion](/images/cleanup-1.png?featherlight=false)
{{% notice info %}}
This stack deletion takes about 5 minutes to complete. It will also delete the other stack that begins with `aws-cloud9-*`.
{{% /notice %}}
Additionally, both the service role (`AWSCloud9SSMAccessRole`) and the IAM instance profile (`AWSCloud9SSMInstanceProfile`) were created automatically for you by the CloudFormation template. The managed policies included in the service role are: `AWSCloud9SSMInstanceProfile` and `AmazonSSMManagedInstanceCore`. These IAM resources do not incur any additional cost to you if left on the account.
{{% notice note %}}
If you no longer need to use Systems Manager to access an instance, you can delete the `AWSCloud9SSMAccessRole` service role. For more information, see [Deleting roles or instance profiles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_manage_delete.html) in the _IAM User Guide_.
{{% /notice %}}
More info on these IAM resources in the [Documentation](https://docs.aws.amazon.com/cloud9/latest/user-guide/ec2-ssm.html#service-role-ssm).

### AWS Key Management Service (KMS)

We also used a KMS Customer Managed Key (CMK) key to encrypt and decrypt data as part of the workshop. You'll want to delete this key directly from the KMS console as follows.

Using the AWS Management Console to delete a KMS CMK:

1. Sign in to the AWS Management Console and open the AWS Key Management Service (AWS KMS) console at [https://console.aws.amazon.com/kms](https://console.aws.amazon.com/kms).

1. To change the AWS Region, use the Region selector in the upper-right corner of the page.

1. In the navigation pane, choose **Customer managed keys**.

1. Choose or select the previously created `my-enclave-key` that was used in the workshop.

1. Choose **Key actions**, **Schedule key deletion**.

1. (Optional) Reduce the waiting period to a minimum of 7 days.

1. Ensure that the **Keys to delete** table only includes the `my-enclave-key` from the workshop.

1. Select **Confirm that you want to schedule these keys for deletion after a X day waiting period**.

1. Choose **Schedule deletion**.

## ...at an AWS event

There is nothing for you to cleanup and we will take care of the rest.

---
### Thank you for exploring the AWS Nitro Enclaves workshop!
