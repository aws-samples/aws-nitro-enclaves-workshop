+++
title = "Cryptographic attestation"
chapter = false
weight = 14
+++


In this section, you will gain experience with a sample sensitive data processing application that makes use of Nitro Enclaves cryptographic attestation and AWS KMS to isolate sensitive data processing within the boundary of your enclave. This sample demonstrates how cryptographic attestation can be used to protect the privacy of sensitive data. Initially, you will build and deploy this sample application without taking advantage of cryptographic attestation in order to understand its operation. In the second phase of this section, you will enable cryptographic attestation and observe how it can be used to enhance the isolation of sensitive data processing workloads in a Nitro Enclave.

### A unique feature on Nitro Enclaves

Using the Nitro Enclaves SDK, an enclave can request a cryptographically signed attestation document from the Nitro Hypervisor that includes its unique measurements. The enclave uses the attestation process to prove its identity and build trust with an external service using a series of measurements that are unique to an enclave.

An enclave's measurements include a series of hashes and platform configuration registers (PCRs) that are unique to the enclave. You've seen some of these measurements before when you built an enclave EIF and saved the measurement values labeled `PCR0`, `PCR1`, & `PCR2`. The complete list of 6 PCRs are:

|PCR|Hash of ...|Description|
|--- |--- |--- |
|PCR0|Enclave image file|A contiguous measure of the contents of the image file, without the section data.|
|PCR1|Linux kernel and bootstrap|A contiguous measurement of the kernel and boot ramfs data.|
|PCR2|Application|A contiguous, in-order measurement of the user applications, without the boot ramfs.|
|PCR3|IAM role assigned to the parent instance|A contiguous measurement of the IAM role assigned to the parent instance. Ensures that the attestation process succeeds only when the parent instance has the correct IAM role.|
|PCR4|Instance ID of the parent instance|A contiguous measurement of the ID of the parent instance. Ensures that the attestation process succeeds only when the parent instance has a specific instance ID.|
|PCR8|Enclave image file signing certificate|A measure of the signing certificate specified for the enclave image file. Ensures that the attestation process succeeds only when the enclave was booted from an enclave image file signed by a specific certificate.|

You can integrate cryptographic attestation with your own applications and also take advantage of pre-built integrations with services such as AWS KMS. AWS KMS is able to validate enclave attestations and provides the attestation-based condition keys `kms:RecipientAttestation:ImageSha384` and `kms:RecipientAttestation:PCR` for use in key policies. These policies ensure that AWS KMS only allows operations using the KMS key if the enclave's attestation document is valid and conforms to the specified conditions.
### Sample sensitive data processing application overview

{{% notice warning %}}
This module is intended to demonstrate the properties of Nitro Enclaves and offer hands-on experience with the Nitro Enclaves development experience. The module is designed as a teaching tool, and it does not represent an example of security best practices for a production Nitro Enclaves application architecture.
{{% /notice %}}

![Architecture diagram](/images/cryptographic-attestation-arch.png)

The application you will build in this module consists of a server component that will run inside your Nitro Enclave and a client component that will be executed on your parent instance. The client component operates in two phases: data preparation and data submission.

In the data preparation phase, the client component of your application reads an input file containing simulated strings that stand in for sensitive values such as credit card or social security numbers. To prepare this data for later processing, the client component selects one of these values at random, encrypts it using an [AWS Key Management Service (KMS)](https://aws.amazon.com/kms/) customer master key (CMK).

In the data submission phase, the client component passes the encrypted value that you prepared previously to the server component running inside your enclave using the secure local vsock channel. The server component takes this value, sets up an end-to-end encrypted connection with KMS through the vsock and a proxy application running on the parent instance, and then decrypts the simulated sensitive value.

{{% notice tip %}}
The business logic of this application is written in Python. If time allows, please review the code at  
`~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/cryptographic-attestation`  
to understand the internal functioning of this sample. The client component that runs on the parent instance is contained within the `client.py` file and the server component that runs inside the enclave is contained within the `server.py` file.
{{% /notice %}}

{{% notice warning %}}
This section expects that you have already compiled the sample application dependencies and built a docker image for the server component of this application that runs inside the enclave. If you have not yet completed this step please return the [prerequisites section of the Getting Started module](../getting-started/prerequisites.html#compile-the-dependencies-for-the-cryptographic-attestation-sample-application) and do so.
{{% /notice %}}

### Create a KMS CMK

To get started, you'll need to create a KMS CMK for use by your application.

To create a KMS CMK using the AWS Management Console:

1. Sign in to the AWS Management Console and open the AWS Key Management Service (AWS KMS) console at [https://console.aws.amazon.com/kms](https://console.aws.amazon.com/kms).

1. To change the AWS Region, use the Region selector in the upper-right corner of the page.

1. In the navigation pane, choose **Customer managed keys**.

1. Choose **Create key**.

1. For **Key type** select **Symmetric**.

1. Choose **Next**.

1. Type the alias `my-enclave-key` for the CMK.

1. (Optional) Type a description for the CMK.

1. (Optional) Type a tag key and an optional tag value. To add more than one tag to the CMK, choose **Add tag**.

1. Choose **Next**.

1. Do not select any IAM users or roles that can administer the CMK.

1. Choose **Next**.

1. Do not select any IAM users or roles that can use the CMK for cryptographic operations

    {{% notice info %}}
The AWS account (root user) has full permissions by default. As a result, any IAM policies can also give users and roles permission to use the CMK for cryptographic operations.
    {{% /notice %}}

1. Choose **Next**.

1. Review the key settings that you chose. You can still go back and change all settings.

1. Choose **Finish** to create the CMK.

### Configure your KMS key policy

Your KMS key policy should now contain a single statement that allows IAM users and roles to be granted access to the key via their IAM policy documents. This statement should look similar to
<pre>
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111122223333:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        }
    ]
</pre>

The IAM principal associated with your Cloud9 Environment is not granted permission in its IAM policies to perform any actions on your CMK. For example, you will be denied if you attempt to view metadata about the key from your Cloud9 terminal by issuing the following command:
```sh
$ aws kms describe-key --key-id "alias/my-enclave-key"
```

In order to enable your Cloud9 environment to use the key to encrypt and decrypt data, you'll configure that permission in the KMS Key Policy directly.

To prepare a new key policy for your CMK:

1. Store the AWS IAM principal and account associated with your Cloud9 environment in an environment variable by executing the following command in your Cloud9 terminal:
    ```sh
    $ export AWS_PRINCIPAL=`aws sts get-caller-identity | jq -r ".Arn"`
    $ export ACCOUNT_ID=`aws sts get-caller-identity | jq -r ".Account"`
    ```

1. Customize a pre-prepared key policy template with these values by executing the following command in your Cloud9 terminal.
    ```sh
    $ sed -e "s|ACCOUNT_ID|${ACCOUNT_ID}|" -e "s|AWS_PRINCIPAL|${AWS_PRINCIPAL}|" key_policy_template.json > key_policy.json
    ```

#### Update the key policy for your CMK:

1. Open the AWS Key Management Service (AWS KMS) console at [https://console.aws.amazon.com/kms](https://console.aws.amazon.com/kms).

1. To change the AWS Region, use the Region selector in the upper-right corner of the page.

1. To view the keys in your account that you create and manage, choose **Customer managed keys** in the navigation pane.

1. In the list of CMKs, choose the alias **my-enclave-key**.

1. Choose the **Key policy** tab.

1. On the **Key policy** tab, you will see the *default view*. To see the key policy document, choose **Switch to policy view**.

    You will see the key policy document. This is *policy view*. In the key policy statements, you can see the principals who have been given access to the CMK by the key policy, and you can see the actions they can perform.

1. In another window, return to your Cloud9 terminal and issue the `ls` command and choose **key_policy.json** with your cursor.

1. Select **Open**.

1. Your new key policy will open in a Cloud9 editor tab. Please select all the text in the window and copy it to your system clipboard.

1. Return to your window with your KMS CMK **Key policy** tab open. Select **Edit**.

1. Delete the entire key policy and paste your new key policy in its place and then choose **Save changes**.

### Build, run, and connect to your enclave in debug mode

1. Create a new terminal tab on your Cloud9 environment.

1. Build your enclave image file by executing the following command:
    ```sh
    $ nitro-cli build-enclave --docker-uri "data-processing:latest" --output-file "data-processing.eif"
    ```

    The **output** should look similar to
    <pre>
    Enclave Image successfully created.
    {
    "Measurements": {
        "HashAlgorithm": "Sha384 { ... }",
        "PCR0": "287b24930a9f0fe14b01a71ecdc00d8be8fad90f9834d547158854b8279c74095c43f8d7f047714e98deb7903f20e3dd",
        "PCR1": "aca6e62ffbf5f7deccac452d7f8cee1b94048faf62afc16c8ab68c9fed8c38010c73a669f9a36e596032f0b973d21895",
        "PCR2": "0315f483ae1220b5e023d8c80ff1e135edcca277e70860c31f3003b36e3b2aaec5d043c9ce3a679e3bbd5b3b93b61d6f"
    }
    }
    </pre>

    <!-- TODO: improve the approach here -->

    {{% notice info %}}
Please be sure to carefully save these measurements for later reference as they are critical for this section.
    {{% /notice %}}


    <!-- Hide vsock-proxy start section as it is done in the previous chapter.

    ### Start your vsock proxy

    The default configuration for the vsock-proxy service permits the enclave to communicate with AWS KMS endpoints in supported regions.

    To start the vsock-proxy service on the parent instance with the default configuration, issue the following command in your Cloud9 terminal:
    ```sh
    $ systemctl start nitro-enclaves-vsock-proxy.service
    ```
    -->

1. Launch your enclave application by executing the following command in your Cloud9 terminal:
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/cryptographic-attestation
    $ nitro-cli run-enclave --debug-mode --cpu-count 2 --memory 2148 --eif-path "./data-processing.eif"
    ```

1. Connect to your enclave console by issuing the following command:
    ```sh
    $ ENCLAVE_ID=`nitro-cli describe-enclaves | jq -r ".[0].EnclaveID"`
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli console --enclave-id ${ENCLAVE_ID}
    ```

    This terminal tab will now display the debug-mode console output of the running enclave.

### Interacting with your enclave application

1. Return to your previous Cloud9 terminal tab and install dependencies by issuing the following command:
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/cryptographic-attestation
    $ pip3 install --user -r "requirements.txt"
    ```

    <!-- TODO: view values.txt -->

1. Select a simulated sensitive value from `values.txt` at random and encrypt it using your KMS CMK by issuing the following command:
    ```sh
    $ python3 client.py --prepare --values "values.txt"  --alias "my-enclave-key"
    ```

    If successful, this command will print the encrypted ciphertext for the selected value and its last four digits to your screen. It will also create a new file, `string.encrypted`, containing the cyphertext.

1. Send this ciphertext to your enclave by issuing the following command:
    ```sh
    $ python3 client.py --submit --ciphertext "string.encrypted"  --alias "my-enclave-key"
    ```

    In your host instance terminal, you'll see that the last 4 digits of the sensitive value are returned to the parent.

### Taking advantage of cryptographic attestation

Now that you have the broad strokes of your application up and running, it is time to take things to the next level. As currently configured, your application has two areas that could notably be improved on in order to isolate the processing of your simulated sensitive value; the parent instance is currently able to view the plaintext sensitive data by a.) viewing the enclave debug console and b.) by decrypting the value itself using your KMS CMK.

Open up your terminal, which you connected to the debug console. You will be able to see information about the process running inside your enclave, including the entire plaintext of the sensitive value you sent into the enclave in ciphertext form.

You could update your enclave application not to print this value to the console. However, your parent instance would still be able to decrypt this value itself using KMS directly. To decrypt the the ciphertext in `string.encrypted`, run the following command in your Cloud9 terminal:

```sh
$ base64 -di string.encrypted > string.encrypted.binary &&
  aws kms decrypt \
  --ciphertext-blob "fileb://string.encrypted.binary" \
  --output "text" \
  --query "Plaintext" | base64 --decode
```

You'll see that this command prints the full plaintext of the simulated sensitive value to the console. This command is using the Cloud9 environment credentials to call KMS directly. It does not depend on the server component running in the enclave at all.

Using AWS Nitro Enclaves cryptographic attestation with AWS KMS, however, you can configure your application so that the parent instance is unable to decrypt the simulated sensitive value while the enclave remains able to. Furthermore, cryptographic attestation can prohibit a user on the parent instance from accessing sensitive data via the enclaves debug console.

For this example, you will use PCR0, which is a unique hash of measurement of your `data-processing.eif` file.

To add attestation conditions to your key policy:

1. Open key_policy.json in your Cloud9 editor.

2. Place your cursor at the end of line 30 (this line currently says `"Resource": "*"`).

3. Enter a `,`

4. Press the return key on your keyboard to start a new line.

5. Copy the following text and paste it into your Cloud9 editor.

    <!-- Please don't change indentation on JSON block below since we are making it neatly copy-pasteable. -->
    ```
    "Condition": {
                  "StringEqualsIgnoreCase": {
                      "kms:RecipientAttestation:PCR0": "EXAMPLEbc2ecbb68ed99a13d7122abfc0666b926a79d5379bc58b9445c84217f59cfdd36c08b2c79552928702EXAMPLE"
                  }
              }
    ```

6. Replace the placeholder value `EXAMPLEbc2ecbb68ed99a13d7122abfc0666b926a79d5379bc58b9445c84217f59cfdd36c08b2c79552928702EXAMPLE` with the PCR0 value that you saved when building your enclave.

    {{% notice tip %}}
If you do not have access to the PCR0 value from building your enclave, you can rebuild your enclave to access this measurement again.
    {{% /notice %}}

To update your key policy:

* Follow the steps in the [update the key policy for your CMK](#update-the-key-policy-for-your-cmk) procedure above.

Your key policy now permits your Cloud9 environment principal to encrypt using the CMK but allows it to decrypt only when the request is accompanied by a signed attestation document that can be obtained only from within the enclave.

### Validating enclave attestation-based KMS key policy conditions

Now that you've updated you key policy, confirm that the new condition has take effect by issuing the following command in your Cloud9 terminal:
```sh
$ base64 -di string.encrypted > string.encrypted.binary &&
  aws kms decrypt \
  --ciphertext-blob "fileb://string.encrypted.binary" \
  --output "text" \
  --query "Plaintext" | base64 --decode    
```

If successful, you'll receive a message about `AccessDeniedException`. This occurs because although your Cloud9 environment principal has permission to decrypt using the key, you've now placed a condition on that permission that it only applies to request coming from an enclave launched with your specific `data-processing.eif` enclave image file.

This change will also impact the behavior of the enclave in debug mode. To validate the behavior, re-submit your encrypted value to the enclave by running the following command in your Cloud9 terminal:
```sh
$ python3 client.py --submit --ciphertext "string.encrypted"  --alias "my-enclave-key"
```
<!-- TODO -- Server.py needs to be cleaned up. The denial is currently crashing the enclave -->

This command fails because the Nitro Hypervisor will not sign an attestation document with actual PCR values for an enclave launched in debug mode.

{{% notice note %}}
Enclaves booted in debug mode generate attestation documents with PCRs that are made up entirely of zeros (`000000000000000000000000000000000000000000000000`). These attestation documents cannot be used for cryptographic attestation.
{{% /notice %}}

To confirm that your enclave is still able to decrypt when launched in production mode:

1. Terminate your enclave by issuing the following command in your Cloud9 terminal:
    ```sh
    $ ENCLAVE_ID=`nitro-cli describe-enclaves | jq -r ".[0].EnclaveID"`
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
    ```

1. Launch the enclave in production mode by issuing the following command in your Cloud9 terminal:
    ```sh
    $ nitro-cli run-enclave --cpu-count 2 --memory 2148 --eif-path "./data-processing.eif"
    ```

1. Submit your encrypted value to the enclave by issuing the following command in a separate Cloud9 terminal window:
    ```sh
    $ cd ~/environment/aws-nitro-enclaves-workshop/resources/code/my-first-enclave/cryptographic-attestation
    $ python3 client.py --submit --ciphertext "string.encrypted"  --alias "my-enclave-key"
    ```

1. Confirm that the last four digits of one of your sensitive values now prints to the console.

Thanks to cryptographic attestation and the KMS condition key you added, a user or process on the parent instance is now unable to access the full plaintext decrypted value either through decrypting the value directly with KMS or through viewing the debug console. When run in production mode the enclave is able to decrypt the simulated sensitive value using KMS and returns only the last 4 digits to the parent instance.

### Modifying the enclave application code

So far in this section, you've explored the base functionality of this sensitive data processing application and how cryptographic attestation can be used to protect against a parent decrypting using its own credentials or gaining access to plaintext sensitive data via the debug console. What if, however, a motivated attacker simply modified an enclave to return plaintext values over the vsock. Let's see what would happen.

The enclave application file `server.py` contains the following code:

```python {linenos=true, linenostart=79}
    last_four = str(plaintext)[-4:]
    r["last_four"] = last_four

c.send(str.encode(json.dumps(r)))

c.close()
```

The trailing `[-4:]` on line 64 of `servery.py` is responsible for ensuring that the program returns only the last four numbers of the plaintext value. To modify this code to return the entire plaintext value to the parent over the vsock, issue the following command in your Cloud9 terminal:

```sh
$ sed -i "s|\[-4:\]||" ./server.py
```

After running this command `server.py` will now look like this:

```python {linenos=true, hl_lines=[1] linenostart=79}
    last_four = str(plaintext)
    r["last_four"] = last_four

c.send(str.encode(json.dumps(r)))

c.close()
```

To run this modified code in the enclave, you'll need to build a new docker image and EIF. To launch an enclave with your modified code:

1. To build a new docker image with your modified code, issue the following command in your Cloud9 terminal:
    ```sh
    $ docker build ./ -t "data-processing-modified"
    ```

1. To build an EIF file from your newly created docker image, issue the following command in your Cloud9 terminal:
    ```sh
    $ nitro-cli build-enclave --docker-uri "data-processing-modified:latest" --output-file "data-processing-modified.eif"
    ```

    {{% notice info %}}
If you carefully note the measurements returned to your terminal window and compare them with the measurements you saved when you first built your `data-processing.eif` file, you'll see that PCRs 0 and 2 now show entirely different values because the application code and thus the image file as a whole have been modified. PCR1 remains unchanged as it reflects a measurement of the kernel and boot ramfs data which have not been changed my your modification.
    {{% /notice %}}

1. Terminate your running enclave by issuing the following command in your Cloud9 terminal:
    ```sh
    $ ENCLAVE_ID=`nitro-cli describe-enclaves | jq -r ".[0].EnclaveID"`
    $ [ "$ENCLAVE_ID" != "null" ] && nitro-cli terminate-enclave --enclave-id ${ENCLAVE_ID}
    ```


1. Launch a new enclave with the EIF you just built by issuing the following command in your Cloud9 terminal:
    ```sh
    $ nitro-cli run-enclave --cpu-count 2 --memory 2148 --eif-path "./data-processing-modified.eif"
    ```

1. Submit your ciphertext to the updated enclave, which is now programmed to return the entire plaintext produced by decrypting the provided ciphertext by issuing the following command in your Cloud9 terminal:
    ```sh
    $ python3 client.py --submit --ciphertext "string.encrypted"  --alias "my-enclave-key"
    ```

Fortunately, the security model of our application protects the privacy of the simulated sensitive value and fails to return the plaintext to the parent instance even after the `server.py` program in the enclave was modified to do so. The reason that the modified program cannot return the plaintext value is that it was unable to decrypt the value in the first place due to cryptographic attestation. When you changed the program and rebuilt the EIF it generated a new PCR0 value. When the enclave program called `KMS:Decrypt` it was denied because the signed attestation document it provided did not contain a PCR0 value that matched the PCR0 for the approved EIF you configured KMS to allow decrypt permission for.

### Summary

In this section, you built, deployed, and tested a sample application that processes encrypted values within an enclave. You then identified opportunities for these plaintext values to be obtained outside of the trusted enclave application and Nitro Enclaves cryptographic attestation and AWS KMS cryptographic attestation condition keys to improving the isolation and confidentiality of your sensitive data processing application.

---
#### Proceed to the [Troubleshooting](troubleshooting.html) section to continue the workshop.
