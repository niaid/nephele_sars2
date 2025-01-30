FROM condaforge/mambaforge:23.3.1-1

RUN apt update && apt upgrade -y
RUN apt install -y build-essential unzip
# RUN DEBIAN_FRONTEND=noninteractive apt-get -y install tzdata

# Install dependencies
RUN mamba install -y -c conda-forge -c bioconda samtools~=1.18 bcftools~=1.17 trimmomatic~=0.39 bwa~=0.7 picard~=3.1 gatk4~=4.5 pilon~=1.24 bedtools~=2.31 deeptools~=3.5 pysam~=0.21 seaborn~=0.13 nextflow=22.10.6 r-base ivar~=1.4 jvarkit awscli
RUN pip install pypairix
RUN wget https://snpeff.blob.core.windows.net/versions/snpEff_latest_core.zip -P /usr/local/src && unzip /usr/local/src/snpEff_latest_core.zip -d /usr/local/src
RUN find /opt/conda/share -name "NexteraPE-PE.fa" -type f 2>/dev/null | xargs -I {} cp {} /usr/local/src/

# Install nephele_pipeline_utils
RUN --mount=type=secret,id=AWS_ACCESS_KEY_ID \
    --mount=type=secret,id=AWS_SECRET_ACCESS_KEY \
    --mount=type=secret,id=AWS_SESSION_TOKEN \
    AWS_ACCESS_KEY_ID=$(cat /run/secrets/AWS_ACCESS_KEY_ID) \
    AWS_SECRET_ACCESS_KEY=$(cat /run/secrets/AWS_SECRET_ACCESS_KEY) \
    AWS_SESSION_TOKEN=$(cat /run/secrets/AWS_SESSION_TOKEN) \
    aws codeartifact login --tool pip --repository nephele --domain nephele --domain-owner 629126632555 --region us-east-1
RUN pip install nephele_pipeline_utils==0.1.42


# Set the working directory for the pipeline
WORKDIR /pipeline

COPY nephele_sars2 .

# Define the entrypoint and command
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]