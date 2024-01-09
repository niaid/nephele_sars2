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
    "inputs": [
        {
            "name": "S27",
            "files": [
                {
                    "path": "example-A_S27_L001_R1_001.fastq.gz",
                    "type": "fwd"
                },
                {
                    "path": "example-A_S27_L001_R2_001.fastq.gz",
                    "type": "rev"
                }

            ],
            "metadata": [{}],
            "type": "fastq",
            "source": "input"
        }
    ],
    "pipeline_arguments": {
        "data_type": "COVID19_PE_ARTIC",
        "primer_reference": "v4_1.bed",
        "ref": "refs/SARS-CoV2.fa",
        "snpeff_data_dir": "snpeff_data"
    },
    "outputs": []
}
```

SGS PE
```
{
    "inputs": [
        {
            "name": "SRR15205494",
            "files": [
                {
                    "path": "example-A_S27_L001_R1_001.fastq.gz",
                    "type": "fwd_a"
                },
                {
                    "path": "example-A_S27_L001_R2_001.fastq.gz",
                    "type": "rev_a"
                },
                {
                    "path": "example-B_S28_L001_R1_001.fastq.gz",
                    "type": "fwd_b"
                },
                {
                    "path": "example-B_S28_L001_R2_001.fastq.gz",
                    "type": "rev_b"
                },
                {
                    "path": "new_A.fa",
                    "type": "primer_a"
                },
                {
                    "path": "new_B.fa",
                    "type": "primer_b"
                }

            ],
            "metadata": [{}],
            "type": "fastq",
            "source": "input"
        }
    ],
    "pipeline_arguments": {
        "data_type": "COVID19_PE",
        "ref": "refs/SARS-CoV2.fa",
        "snpeff_data_dir": "snpeff_data"
    },
    "outputs": []
}
```