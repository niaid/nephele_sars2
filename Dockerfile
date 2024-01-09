# Use a desired base image, for example:
FROM python:3.9
ARG AWS_ACCESS_KEY_ID 
ARG AWS_SECRET_ACCESS_KEY 
ARG AWS_SESSION_TOKEN
# Install required system packages, for example:
RUN apt-get update && apt-get install -y awscli

# Install other tools that the pipeline needs, for example:
RUN git clone https://github.com/bonsai-team/Porechop_ABI.git && \
    cd Porechop_ABI && \
    pip install .

# Install nephele_pipeline_utils: aws codeartifact login --tool pip --repository nephele --domain nephele --domain-owner 566113047672 --region us-east-1
RUN AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} aws codeartifact login --tool pip --repository nephele --domain nephele --domain-owner 629126632555 --region us-east-1
RUN pip install nephele_pipeline_utils==0.1.3 psutil

# Set working directory and copy necessary files, for example:
WORKDIR /pipeline
COPY nephele_template_pipeline/* .

# Define the entrypoint and command
ENTRYPOINT ["python", "main.py"]
# ENTRYPOINT [ "bash" ]
CMD ["--help"]
