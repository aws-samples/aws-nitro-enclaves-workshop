# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# // SPDX-License-Identifier: MIT-0

FROM public.ecr.aws/amazonlinux/amazonlinux:minimal

# Install python for running the server
RUN dnf install python3 -y

WORKDIR /app

COPY server.py ./

CMD ["python3" , "/app/server.py"]
