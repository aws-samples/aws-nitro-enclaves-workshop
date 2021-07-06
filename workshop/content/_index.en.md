+++
title = "AWS Nitro Enclaves Workshop"
chapter = true
weight = 1
+++


# AWS Nitro Enclaves Workshop

![AWS Nitro Enclaves Splash Image](/images/nitro-enclaves.png?featherlight=false)

_Learn how to use AWS Nitro Enclaves to process highly sensitive data_
## What is AWS Nitro Enclaves?

AWS Nitro Enclaves enables customers to create isolated compute environments to further protect and securely process highly sensitive data such as personally identifiable information (PII), healthcare, financial, and intellectual property data within their Amazon EC2 instances. Nitro Enclaves uses the same Nitro Hypervisor technology that provides CPU and memory isolation for EC2 instances.

Nitro Enclaves helps customers reduce the attack surface area for their most sensitive data processing applications. Enclaves offers an isolated, hardened, and highly constrained environment to host security-critical applications. They have no persistent storage, no interactive access, and no external networking. Communication between your instance and your enclave is done using a secure local channel. By default, even a root user or an admin user on the instance will not be able to access or SSH into the enclave. Nitro Enclaves includes cryptographic attestation for your software, so that you can be sure that only authorized code is running, as well as integration with the AWS Key Management Service, so that only your enclaves can access sensitive material.

[Official Documentation](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html)

{{% notice warning %}}
This workshop will create AWS resources and you may incur additional charges if these resources are left in your AWS account.  
Please refer to cleanup procedures <!--in each section--> of the workshop and review all the resources created<!-- by automated stacks-->.
{{% /notice %}}

---
#### Proceed to the [Getting Started](getting-started.html) module to begin.