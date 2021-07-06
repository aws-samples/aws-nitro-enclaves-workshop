# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# // SPDX-License-Identifier: MIT-0

FROM public.ecr.aws/amazonlinux/amazonlinux:2

# Install python for running the server
RUN yum install python3 -y

WORKDIR /app

COPY server.py ./

CMD ["python3" , "/app/server.py"]
