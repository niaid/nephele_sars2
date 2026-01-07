# Nephele SARS-CoV-2 pipeline

## Introduction
This pipeline assembles SARS-CoV-2 genome and calls mutations from Illumina sequence data generated using a tiled multiplexed primers strategy (example: Artic protocol). Users can select from primers such as ARTIC and NEB-Varskip. Alternatively, users can upload a custom primers design (in .bed format)

## Datafiles
https://main.nephele.niaiddev.net/select_or_upload_primer_file
- ref_db_path
  - /dbs/SARS-CoV2/refs
- snpeff_db_path
  - /dbs/SARS-CoV2/snpeff_data
- primer_file_path (one of the below choices)
  - ARTIC
    - V1: /dbs/SARS-CoV2/artic_primer/v1.bed
    - V2: /dbs/SARS-CoV2/artic_primer/v2.bed
    - V3: /dbs/SARS-CoV2/artic_primer/v3.bed
    - V4: /dbs/SARS-CoV2/artic_primer/v4.bed
    - V4.1: /dbs/SARS-CoV2/artic_primer/v4_1.bed
    - V5.0.0_400: /dbs/SARS-CoV2/artic_primer/v5_0_0_400.bed
    - V5.1.0_400: /dbs/SARS-CoV2/artic_primer/v5_1_0_400.bed
    - V5.2.0_400: /dbs/SARS-CoV2/artic_primer/v5_2_0_400.bed
    - V5.2.0_1200: /dbs/SARS-CoV2/artic_primer/v5_2_0_1200.bed
    - V5.3.2_400: /dbs/SARS-CoV2/artic_primer/v5_3_2_400.bed
  - NEB
    - VarSkip Short V1a: /dbs/SARS-CoV2/artic_primer/neb_vss1a.primer.bed
    - VarSkip Short V2a: /dbs/SARS-CoV2/artic_primer/neb_vss2a.primer.bed
    - VarSkip Long V1a: /dbs/SARS-CoV2/artic_primer/neb_vsl1a.primer.bed
  - IDT
    - Midnight 1200: /dbs/SARS-CoV2/artic_primer/midnight1200.bed
  - Custom
    - Upload your own primer file in bed format