FROM condaforge/mambaforge:23.3.1-1
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_SESSION_TOKEN

RUN apt update && apt upgrade -y
RUN apt install -y build-essential unzip
# RUN DEBIAN_FRONTEND=noninteractive apt-get -y install tzdata

# Install dependencies
RUN mamba install -y -c conda-forge -c bioconda samtools bcftools trimmomatic bwa picard gatk4 pilon bedtools deeptools pysam seaborn nextflow=22.10.6 r-base ivar jvarkit awscli
RUN pip install pypairix
RUN wget https://snpeff.blob.core.windows.net/versions/snpEff_latest_core.zip -P /usr/local/src && unzip /usr/local/src/snpEff_latest_core.zip -d /usr/local/src
RUN find /opt/conda/share -name "NexteraPE-PE.fa" -type f 2>/dev/null | xargs -I {} cp {} /usr/local/src/

# Install nephele_pipeline_utils: aws codeartifact login --tool pip --repository nephele --domain nephele --domain-owner 566113047672 --region us-east-1
RUN AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} aws codeartifact login --tool pip --repository nephele --domain nephele --domain-owner 629126632555 --region us-east-1
RUN pip install nephele_pipeline_utils


# Set the working directory for the pipeline
WORKDIR /pipeline

COPY nephele_sars2 .

# Define the entrypoint and command
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]