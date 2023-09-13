# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# // SPDX-License-Identifier: MIT-0

#vsock demo image
FROM public.ecr.aws/amazonlinux/amazonlinux:minimal

# Install python for running the server and net-tools for modifying network config
RUN dnf install python3 iproute   -y

WORKDIR /app

COPY server.py ./
COPY traffic_forwarder.py ./
COPY run.sh ./

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]