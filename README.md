# Nephele SARS-CoV-2 pipeline

## Introduction
This pipeline assembles SARS-CoV-2 genome and calls mutations from Illumina sequence data generated using a tiled multiplexed primers strategy (example: Artic protocol). Users can select from primers such as ARTIC and NEB-Varskip. Alternatively, users can upload a custom primers design (in .bed format)

## Datafiles
TODO: Provide links to download these files
- refs/SARS-CoV2.fa (and index files)
- snpeff_data
- primer file (only for ARTIC protocol)

## Sample input.json

ARTIC PE
```
{
    "samples": [
        {
            "id": "S27",
            "forward_fastq_file_path": "/inputs/example-A_S27_L001_R1_001.fastq.gz",
            "reverse_fastq_file_path": "/inputs/example-A_S27_L001_R2_001.fastq.gz"
        },
        {
            "id": "S28",
            "forward_fastq_file_path": "/inputs/example-B_S28_L001_R1_001.fastq.gz",
            "reverse_fastq_file_path": "/inputs/example-B_S28_L001_R2_001.fastq.gz"
        }
    ],
    "pipeline_arguments": {
        "data_type": "COVID19_PE_ARTIC",
        "primer_reference": "/dbs/v4_1.bed",
        "ref": "/dbs/refs/SARS-CoV2.fa",
        "snpeff_data_dir": "/dbs/snpeff_data"
    }
}
```

SGS PE
```
{
    "samples": [
        {
            "id": "S27",
            "forward_fastq_file_a_path": "/inputs/example-A_S27_L001_R1_001.fastq.gz",
            "reverse_fastq_file_a_path": "/inputs/example-A_S27_L001_R2_001.fastq.gz",
            "forward_fastq_file_b_path": "/inputs/example-B_S28_L001_R1_001.fastq.gz",
            "reverse_fastq_file_b_path": "/inputs/example-B_S28_L001_R2_001.fastq.gz",
            "primer_file_a": "/inputs/new_A.fa",
            "primer_file_b": "/inputs/new_B.fa"
        }
    ],
    "pipeline_arguments": {
        "data_type": "COVID19_PE",
        "ref": "/dbs/refs/SARS-CoV2.fa",
        "snpeff_data_dir": "/dbs/snpeff_data"
    }
}
```